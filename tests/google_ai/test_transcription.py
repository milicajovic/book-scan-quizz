import unittest
import os
from google_ai import transcribe_audio
from tests.test_config import DUMMY_SERBIAN
from app import create_app
from config import config


class TestTranscription(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_transcribe_dummy_serbian(self):
        # Ensure the test file exists
        self.assertTrue(os.path.exists(DUMMY_SERBIAN), f"Test file not found: {DUMMY_SERBIAN}")

        result = transcribe_audio(DUMMY_SERBIAN)

        # Assert that we got a non-None result
        self.assertIsNotNone(result, "Transcription result is None")

        # Assert that the result is a non-empty string
        self.assertTrue(isinstance(result, str) and len(result) > 0, "Transcription result is empty or not a string")

        # You might want to add more specific assertions here based on what you expect
        # the transcription of dummy_serbian.wav to contain
        # For example:
        # self.assertIn("expected word or phrase", result.lower())

        print(f"Transcription result: {result}")


if __name__ == '__main__':
    unittest.main()
# This file is intentionally left empty