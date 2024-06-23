from flask import render_template, request, jsonify
from . import quiz
from ..utils import transcribe_audio


@quiz.route('/')
def index():
    return render_template('quiz/index.html')


@quiz.route('/evaluate_audio', methods=['POST'])
def evaluate_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']

    if audio_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if audio_file:
        result = transcribe_audio(audio_file)
        return jsonify({'result': result})