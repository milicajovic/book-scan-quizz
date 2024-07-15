import os

# Get the absolute path to the test directory
TEST_DIR = os.path.dirname(os.path.abspath(__file__))

# Define paths to test files
TEST_FILES_DIR = os.path.join(TEST_DIR, 'files')
TEST_AUDIO_DIR = os.path.join(TEST_FILES_DIR, 'audio')
TEST_IMAGES_DIR = os.path.join(TEST_FILES_DIR, 'images')

# Define specific test file paths
DUMMY_SERBIAN = os.path.join(TEST_AUDIO_DIR, 'dummy_serbian.wav')
GERMAN_WRONG = os.path.join(TEST_AUDIO_DIR, 'german_wrong_sentence.wav')
PHOTOSYNTHESIS_AUDIO = os.path.join(TEST_AUDIO_DIR, 'dummy_serbian.wav')
EMPTY_AUDIO = os.path.join(TEST_AUDIO_DIR, 'no_text_audio.wav')

# You can add more configurations here as needed