import unittest
import os
from pathlib import Path
from flask import current_app
from google_ai import generate_questions, config
from tests.test_config import TEST_IMAGES_DIR
from app import create_app
from config import TestingConfig


class TestQuestionGenerator(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()

        self.image_files = [
            os.path.join(TEST_IMAGES_DIR, f)
            for f in os.listdir(TEST_IMAGES_DIR)
            if f.lower().endswith(('.png', '.jpg', '.jpeg'))
        ]
        self.single_image = self.image_files[0] if self.image_files else None

    def tearDown(self):
        self.app_context.pop()

    def test_generate_questions_single_image(self):
        if not self.single_image:
            self.skipTest("No test images available")

        questions = generate_questions([self.single_image])
        self.assertIsNotNone(questions)
        self.assertIsInstance(questions, list)
        self.assertTrue(len(questions) > 0)

        for question in questions:
            self._assert_valid_question(question)
            print(question)

    def test_generate_questions_multiple_images(self):
        if len(self.image_files) < 2:
            self.skipTest("Not enough test images available")

        questions = generate_questions(self.image_files[:2])
        self.assertIsNotNone(questions)
        self.assertIsInstance(questions, list)
        self.assertTrue(len(questions) > 0)

        for question in questions:
            self._assert_valid_question(question)
            print(question)

    def test_generate_questions_invalid_image(self):
        invalid_file = os.path.join(TEST_IMAGES_DIR, 'nonexistent.jpg')
        with self.assertRaises(Exception):  # Adjust the exception type as needed
            generate_questions([invalid_file])

    def _assert_valid_question(self, question):
        self.assertIsInstance(question, dict)
        self.assertIn('page_nr', question)
        self.assertIn('question', question)
        self.assertIn('answer', question)
        self.assertIn('difficulty_level', question)

        self.assertIsInstance(question['page_nr'], int)
        self.assertIsInstance(question['question'], str)
        self.assertIsInstance(question['answer'], str)
        self.assertIn(question['difficulty_level'], ['easy', 'medium', 'hard'])

        self.assertTrue(len(question['question']) > 0)
        self.assertTrue(len(question['answer']) > 0)

    def test_generate_questions_respects_model_config(self):
        if not self.single_image:
            self.skipTest("No test images available")

        original_model = config.DEFAULT_PRO_MODEL
        config.DEFAULT_PRO_MODEL = "test-model"

        try:
            with unittest.mock.patch('google_ai.question_generator.execute_genai_operation') as mock_execute:
                mock_execute.return_value = '[{"page_nr": 1, "question": "Test?", "answer": "Test.", "difficulty_level": "easy"}]'
                generate_questions([self.single_image])
                mock_execute.assert_called_once()
                _, kwargs = mock_execute.call_args
                self.assertEqual(kwargs['model_name'], "test-model")
        finally:
            config.DEFAULT_PRO_MODEL = original_model


if __name__ == '__main__':
    unittest.main()