import unittest
import os
from google_ai.audio_answer_evaluator import evaluate_audio_answer
from google.api_core import exceptions
from flask import current_app
from app import create_app
from tests.test_config import PHOTOSYNTHESIS_AUDIO


class TestAudioAnswerEvaluatorIntegration(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()

        self.question = "What is photosynthesis?"
        self.correct_answer = ("Photosynthesis is the process by which plants use sunlight to convert water and "
                               "carbon dioxide into oxygen and glucose.")
        self.audio_path = PHOTOSYNTHESIS_AUDIO

    def tearDown(self):
        self.app_context.pop()

    def test_evaluate_audio_answer(self):
        try:
            result = list(evaluate_audio_answer(self.question, self.correct_answer, self.audio_path))

            print(result)
            # Check if we got a non-empty result
            self.assertTrue(len(result) > 0)

            # Check if the result contains expected parts
            full_response = ''.join(result)
            self.assertIn('####', full_response)

            # Check if Correctness and Completeness scores are present
            #self.assertRegex(full_response, r'Correctness:\d+')
            #self.assertRegex(full_response, r'Completeness:\d+')

            # Print the full response for manual inspection
            print("Full response:")
            print(full_response)

        except exceptions.GoogleAPICallError as e:
            self.fail(f"Google API call failed: {str(e)}")
        except Exception as e:
            self.fail(f"Unexpected error occurred: {str(e)}")

    def test_file_not_found(self):
        non_existent_path = "non_existent_file.wav"
        result = list(evaluate_audio_answer(self.question, self.correct_answer, non_existent_path))
        self.assertEqual(result, ["Error: Audio file not found."])


if __name__ == '__main__':
    unittest.main()