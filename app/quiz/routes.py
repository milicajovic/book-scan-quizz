from flask import render_template, request, jsonify, current_app
from . import quiz
from ..utils import transcribe_audio


@quiz.route('/')
def index():
    return render_template('quiz/index.html')

@quiz.route('/evaluate_audio', methods=['POST'])
def evaluate_audio():
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400

        audio_file = request.files['audio']

        if audio_file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if audio_file:
            result = transcribe_audio(audio_file)
            return jsonify({'result': result})
        else:
            return jsonify({'error': 'Invalid file'}), 400

    except Exception as e:
        current_app.logger.error(f"Error in evaluate_audio: {str(e)}")
        return jsonify({'error': 'An error occurred while processing the audio 2 '+str(e)}), 500
