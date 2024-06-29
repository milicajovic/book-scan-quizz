import os
import json


def should_exclude(path):
    exclude_dirs = {'.venv', 'venv', '__pycache__', 'node_modules', '.git', 'audio_uploads' , '.idea'}
    exclude_extensions = {'.pyc', '.pyo', '.pyd', '.db', '.sqlite3', 'wav', 'pdf', 'png', 'jpg', 'jpeg', 'json'}

    parts = path.split(os.sep)
    if any(part in exclude_dirs for part in parts):
        return True

    _, ext = os.path.splitext(path)
    return ext.lower() in exclude_extensions


def read_file_content(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"


def explore_directory(directory):
    structure = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if not should_exclude(file_path):
                relative_path = os.path.relpath(file_path, directory)
                structure.append({
                    'path': relative_path,
                    'content': read_file_content(file_path)
                })
    return structure


def export_project_structure(root_dir='.'):

    if os.path.exists('project_structure.json'):
        os.remove('project_structure.json')

    project_structure = explore_directory(root_dir)
    output = {
        'project_structure': project_structure
    }

    with open('project_structure.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)


if __name__ == "__main__":
    export_project_structure()
    print("Project structure exported to project_structure.json")