import os


def create_directory_structure():
    base_dir = '.'

    # Create main directory structure
    directories = [
        '',
        'app',
        'app/main',
        'app/auth',
        'app/quiz',
        'app/models',
        'app/static',
        'app/templates',
        'tests'
    ]

    for directory in directories:
        os.makedirs(os.path.join(base_dir, directory), exist_ok=True)

    # Create files
    files = [
        'app/__init__.py',
        'app/main/__init__.py',
        'app/main/routes.py',
        'app/main/errors.py',
        'app/auth/__init__.py',
        'app/auth/routes.py',
        'app/quiz/__init__.py',
        'app/quiz/routes.py',
        'app/models/__init__.py',
        'app/utils.py',
        'tests/__init__.py',
        'tests/test_main.py',
        'tests/test_auth.py',
        'tests/test_quiz.py',
        'config.py',
        'run.py',
        'requirements.txt'
    ]

    for file in files:
        open(os.path.join(base_dir, file), 'a').close()

    print("Directory structure created successfully!")


if __name__ == "__main__":
    create_directory_structure()