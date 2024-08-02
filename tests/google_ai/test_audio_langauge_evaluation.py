import unittest
import os
from google_ai.audio_answer_evaluator import evaluate_audio_answer
from google.api_core import exceptions
from flask import current_app
from app import create_app
from google_ai.evaluate_language_audio import evaluate_language_audio
from tests.test_config import PHOTOSYNTHESIS_AUDIO, EMPTY_AUDIO, TEST_AUDIO_DIR


class TestAudioLanguageEvaluator(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()

        self.question = "Say 'Hello, how are you?' in German"
        self.audio_path = os.path.join(TEST_AUDIO_DIR, 'german_howareyou.wav')
        self.empty_audio_file = EMPTY_AUDIO

    def tearDown(self):
        self.app_context.pop()

    def test_evaluate_audio_answer(self):
        try:
            result = list(evaluate_language_audio("English",
                                                  "German",
                                                  self.question, self.audio_path))

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

    def test_empty_audio_(self):
        try:
            #question = "In welchem Jahr startete die französische Armee ihren Russlandfeldzug?"
            #answer = "1812"
            question = "Wie heißt die Schlacht, die in der Nähe von Wien stattfand?"
            answer = "Wagram"
            result = list(evaluate_audio_answer(question, answer, self.empty_audio_file))

            print(result)
            # Check if we got a non-empty result
            self.assertTrue(len(result) > 0)

            # Check if the result contains expected parts
            full_response = ''.join(result)
            #self.assertIn('####', full_response)

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