import unittest
import os
from transcribe import transcribe_audio
from app import create_app
from config import config


class TestTranscribe(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_transcribe_file(self):
        # Get the absolute path to the test file using the app config
        test_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      "..",
                                      self.app.config['UPLOAD_FOLDER'],
                                      "test_prompt.wav")

        # Ensure the test file exists
        self.assertTrue(os.path.exists(test_file_path), f"Test file not found: {test_file_path}")

        result = transcribe_audio(test_file_path)
        print(result)
        self.assertIsInstance(result, str)


if __name__ == '__main__':
    unittest.main()