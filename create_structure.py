import os

def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Created directory: {path}")

def create_file(path):
    if not os.path.exists(path):
        with open(path, 'w') as f:
            f.write("# This file is intentionally left empty")
        print(f"Created file: {path}")

def generate_structure():
    # Define the base directories
    base_dir = os.path.dirname(os.path.abspath(__file__))
    google_ai_dir = os.path.join(base_dir, 'google_ai')
    tests_dir = os.path.join(base_dir, 'tests')
    tests_google_ai_dir = os.path.join(tests_dir, 'google_ai')

    # Create directories
    create_directory(google_ai_dir)
    create_directory(tests_dir)
    create_directory(tests_google_ai_dir)

    # Create files in google_ai directory
    create_file(os.path.join(google_ai_dir, '__init__.py'))
    create_file(os.path.join(google_ai_dir, 'transcription.py'))
    create_file(os.path.join(google_ai_dir, 'question_generator.py'))
    create_file(os.path.join(google_ai_dir, 'file_utils.py'))

    # Create files in tests/google_ai directory
    create_file(os.path.join(tests_google_ai_dir, '__init__.py'))
    create_file(os.path.join(tests_google_ai_dir, 'test_transcription.py'))
    create_file(os.path.join(tests_google_ai_dir, 'test_question_generator.py'))
    create_file(os.path.join(tests_google_ai_dir, 'test_file_utils.py'))

    print("File structure generated successfully!")

if __name__ == "__main__":
    generate_structure()