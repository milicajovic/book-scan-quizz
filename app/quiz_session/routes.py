import html
import os
from datetime import datetime

from flask import jsonify, current_app
from flask import render_template, redirect, url_for
from flask import request, Response, stream_with_context
from flask_login import current_user
from flask_login import login_required
from werkzeug.utils import secure_filename

from google_ai.audio_answer_evaluator import evaluate_audio_answer
from . import quiz_session
from .. import db
from ..models import Question, PrepSession, Answer
from ..models import Quiz


@quiz_session.route('/start/<quiz_id>')
@login_required
def start(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    existing_session = PrepSession.query.filter_by(
        user_id=current_user.id,
        quiz_id=quiz_id,
        status='in_progress'
    ).first()

    if existing_session:
        return redirect(url_for('quiz_session.answer_question', session_id=existing_session.id))

    new_session = PrepSession(user_id=current_user.id, quiz_id=quiz_id, status='in_progress')
    db.session.add(new_session)
    db.session.commit()
    return redirect(url_for('quiz_session.answer_question', session_id=new_session.id))


@quiz_session.route('/answer/<session_id>', methods=['GET', 'POST'])
@login_required
def answer_question(session_id):
    prep_session = PrepSession.query.get_or_404(session_id)
    if prep_session.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    current_question = prep_session.get_current_question()
    if not current_question:
        prep_session.status = 'completed'
        db.session.commit()
        return redirect(url_for('quiz_session.complete', session_id=session_id))

    return render_template('quiz_session/answer_question.html', question=current_question, session_id=session_id)


@quiz_session.route('/complete/<session_id>')
@login_required
def complete(session_id):
    prep_session = PrepSession.query.get_or_404(session_id)
    if prep_session.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    prep_session.status = 'completed'
    db.session.commit()

    return render_template('quiz_session/complete.html', session=prep_session)


def validate_input(audio_file, question_id, session_id):
    if not audio_file or not question_id or not session_id:
        return jsonify({'error': 'Missing required data'}), 400

    audio_data = audio_file.read()
    if len(audio_data) == 0:
        return jsonify({'error': 'Audio data is empty'}), 400

    question = Question.query.get(question_id)
    prep_session = PrepSession.query.get(session_id)

    if not question or not prep_session:
        return jsonify({'error': 'Question or session not found'}), 404

    return audio_data, question, prep_session


def process_audio_file(audio_data, original_filename):
    # Get the file extension from the original filename
    _, file_extension = os.path.splitext(original_filename)

    # Create a timestamp with milliseconds
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]

    # Create a new filename
    new_filename = f"audio_{timestamp}{file_extension}"

    # Get the UPLOAD_FOLDER from the app config
    upload_folder = current_app.config['UPLOAD_FOLDER']

    # Ensure the upload folder exists
    os.makedirs(upload_folder, exist_ok=True)

    # Create the full path for the new file
    audio_file_path = os.path.join(upload_folder, new_filename)

    # Write the audio data to the file
    with open(audio_file_path, 'wb') as audio_file:
        audio_file.write(audio_data)

    current_app.logger.info(f"Audio file created: {audio_file_path}")
    return audio_file_path


def generate_evaluation(question, audio_file_path):
    if not os.path.exists(audio_file_path):
        yield html.escape(f"Error: Audio file not found: {audio_file_path}")
        return

    try:
        for chunk in evaluate_audio_answer(question.question_text, question.answer, audio_file_path):
            yield chunk
    except Exception as e:
        error_message = f"Error in generate_evaluation: {str(e)}"
        current_app.logger.error(error_message)
        yield html.escape(error_message)


@quiz_session.route('/evaluate_audio', methods=['POST'])
@login_required
def evaluate_audio():
    audio_file_path = None
    try:
        audio_file = request.files.get('audio')
        question_id = request.form.get('question_id')
        session_id = request.form.get('session_id')

        if not audio_file or not question_id or not session_id:
            return jsonify({'error': 'Missing required data'}), 400

        question = Question.query.get(question_id)
        prep_session = PrepSession.query.get(session_id)

        validate_input(audio_file, question, prep_session)
        audio_file_path = process_audio_file(audio_file)
        current_app.logger.info(f"Audio file processed: {audio_file_path}")

        def generate():
            try:
                yield from generate_evaluation(question, audio_file_path)
            finally:
                store_answer(current_user.id, question.id, prep_session.id, os.path.basename(audio_file_path))
                if audio_file_path and os.path.exists(audio_file_path):
                    try:
                        os.remove(audio_file_path)
                        current_app.logger.info(f"Audio file deleted: {audio_file_path}")
                    except Exception as e:
                        current_app.logger.warning(f"Failed to delete audio file {audio_file_path}: {str(e)}")

        return Response(stream_with_context(generate()), content_type='text/plain')

    except Exception as e:
        error_message = f"Error in evaluate_audio: {str(e)}"
        current_app.logger.exception(error_message)
        return Response(html.escape(error_message), status=200, content_type='text/plain')


def process_audio_file(audio_file):
    filename = secure_filename(audio_file.filename)
    audio_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    audio_file.save(audio_file_path)
    return audio_file_path


def store_answer(user_id, question_id, prep_session_id, audio_filename):
    answer = Answer(
        user_id=user_id,
        question_id=question_id,
        prep_session_id=prep_session_id,
        answer_text="Audio answer provided",
        audio_file_name=audio_filename,
        feedback="Evaluation completed"
    )
    db.session.add(answer)
    db.session.commit()
    current_app.logger.info("Answer stored in database")
