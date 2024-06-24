from flask import render_template, request, jsonify, current_app
from werkzeug.utils import secure_filename
from datetime import datetime
from transcribe import transcribe_audio
from . import quiz
import os

@quiz.route('/')
def index():
    return render_template('quiz/index.html')

def generate_timestamp_filename(original_filename):
    # Get current timestamp with milliseconds
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    # Get the file extension
    _, file_extension = os.path.splitext(original_filename)
    # Create new filename
    return f"{timestamp}{file_extension}"


@quiz.route('/evaluate_audio', methods=['POST'])
def evaluate_audio():
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400

        audio_file = request.files['audio']

        if audio_file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if audio_file:
            # Generate a new filename based on current timestamp
            new_filename = generate_timestamp_filename(audio_file.filename)

            # Secure the filename
            secure_name = secure_filename(new_filename)

            # Define the path where you want to save the file
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], secure_name)

            # Save the file
            audio_file.save(save_path)

            # Now pass the saved file path to your transcribe_audio function
            result = transcribe_audio(save_path)

            # You might want to store the filename in your database here

            return jsonify({'result': result, 'filename': secure_name})
        else:
            return jsonify({'error': 'Invalid file'}), 400

    except Exception as e:
        current_app.logger.error(f"Error in evaluate_audio: {str(e)}")
        return jsonify({'error': f'An error occurred while processing the audio: {str(e)}'}), 500