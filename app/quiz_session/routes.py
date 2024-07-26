import html
import os
from datetime import datetime
from typing import Optional

from flask import current_app, jsonify, Response, stream_with_context
from flask import make_response
from flask import render_template, redirect, url_for
from flask import request
from flask_login import current_user
from flask_login import login_required
from werkzeug.exceptions import NotFound
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

    answered_count = prep_session.get_distinct_answered_questions_count()
    total_count = prep_session.get_total_quiz_questions_count()

    if total_count == 0:
        current_app.logger.error(f"Quiz {prep_session.quiz_id} has no questions")
        raise NotFound("This quiz has no questions. Please contact the administrator.")

    if answered_count >= total_count:
        return redirect(url_for('quiz_session.complete', session_id=session_id))

    current_question = prep_session.get_current_question()
    if not current_question:
        current_app.logger.error(f"No question found for session {session_id} when one was expected")
        raise NotFound("No question found when one was expected. The quiz may be in an inconsistent state.")

    progress_percentage = (answered_count / total_count) * 100

    return render_template('quiz_session/answer_question.html',
                           question=current_question,
                           session_id=session_id,
                           progress_percentage=progress_percentage,
                           answered_count=answered_count,
                           total_count=total_count)

@quiz_session.route('/speech-to-text')
@login_required
def speech_to_text():
    return render_template('quiz_session/speech_to_text.html')

@quiz_session.route('/complete/<session_id>')
@login_required
def complete(session_id):
    prep_session = PrepSession.query.get_or_404(session_id)
    if prep_session.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    # Get counts using the new methods
    answered_questions_count = prep_session.get_distinct_answered_questions_count()
    total_questions_count = prep_session.get_total_quiz_questions_count()

    # Check if all questions have been answered
    if answered_questions_count == total_questions_count:
        prep_session.status = 'completed'
        db.session.commit()

    # Fetch all answers with their related questions, ordered by question position
    answers = Answer.query.join(Question)\
        .filter(Answer.prep_session_id == prep_session.id)\
        .order_by(Question.position, Answer.id)\
        .all()

    response = make_response(render_template('quiz_session/complete.html',
                                             session=prep_session,
                                             answers=answers,
                                             answered_questions_count=answered_questions_count,
                                             total_questions_count=total_questions_count))
    return response

def validate_input(audio_file, question_id, session_id, current_user_id):
    if not audio_file or not question_id or not session_id:
        raise RuntimeError("Missing required data: audio file, question ID, or session ID")

    if len(audio_file.read()) == 0:
        audio_file.seek(0)  # Reset file pointer
        raise RuntimeError("Audio data is empty")

    audio_file.seek(0)  # Reset file pointer

    question = Question.query.get(question_id)
    if not question:
        raise RuntimeError(f"Question not found: {question_id}")

    prep_session = PrepSession.query.get(session_id)
    if not prep_session:
        raise RuntimeError(f"Prep session not found: {session_id}")

    if prep_session.user_id != current_user_id:
        raise RuntimeError("Unauthorized access to prep session")

    return question, prep_session


def process_audio_file(audio_data):
    original_filename = secure_filename(audio_data.filename)
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
    audio_data.save(audio_file_path)

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


def parse_score(score_str: str) -> Optional[float]:
    """Parse a score string into a float."""
    try:
        return float(score_str)
    except ValueError:
        current_app.logger.warning(f"Invalid score: {score_str}")
        return None


def extract_feedback_and_scores(full_response: str) -> tuple[str, float, float]:
    """
    Extracts feedback, correctness score, and completeness score from the AI response.

    Args:
    full_response (str): The complete response string from the AI.

    Returns:
    tuple: Contains feedback (str), correctness score (float), and completeness score (float).
    """
    parts = full_response.split('####')

    if len(parts) < 2:
        current_app.logger.warning("Response does not contain expected '####' separator")
        return "", 0.0, 0.0

    feedback = parts[0].strip()
    scores_part = parts[1].strip()

    correctness = 0.0
    completeness = 0.0

    for score in scores_part.split():
        key, _, value = score.lower().partition(':')
        if key == 'correctness':
            correctness = parse_score(value) or 0.0
        elif key == 'completeness':
            completeness = parse_score(value) or 0.0
        else:
            current_app.logger.warning(f"Unknown score type: {key}")

    return feedback, correctness, completeness


def generate_audio_evaluation(question, audio_file_path, user_id, prep_session_id):
    full_response = ""

    try:
        for chunk in generate_evaluation(question, audio_file_path):
            full_response += chunk
            yield chunk

        feedback, correctness, completeness = extract_feedback_and_scores(full_response)
        store_answer(user_id, question.id, prep_session_id, os.path.basename(audio_file_path),
                     feedback, correctness, completeness)

    finally:

        if audio_file_path and os.path.exists(audio_file_path):
            try:
                # os.remove(audio_file_path)
                current_app.logger.info(f"Audio file deleted: {audio_file_path}")
            except Exception as e:
                current_app.logger.warning(f"Failed to delete audio file {audio_file_path}: {str(e)}")


@quiz_session.route('/evaluate_audio', methods=['POST'])
@login_required
def evaluate_audio():
    audio_file_path = None
    try:
        audio_file = request.files.get('audio')
        question_id = request.form.get('question_id')
        session_id = request.form.get('session_id')

        question, prep_session = validate_input(audio_file, question_id, session_id, current_user.id)

        audio_file_path = process_audio_file(audio_file)
        current_app.logger.info(f"Audio file processed: {audio_file_path}")

        return Response(
            stream_with_context(generate_audio_evaluation(
                question, audio_file_path, current_user.id, prep_session.id
            )),
            content_type='text/plain'
        )

    except Exception as e:
        error_message = f"Error in evaluate_audio: {str(e)}"
        current_app.logger.exception(error_message)
        return jsonify({'error': error_message}), 500
    # finally:
    #     if audio_file_path and os.path.exists(audio_file_path):
    #         try:
    #             os.remove(audio_file_path)
    #             current_app.logger.info(f"Audio file deleted in finally block: {audio_file_path}")
    #         except Exception as e:
    #             current_app.logger.warning(f"Failed to delete audio file in finally block {audio_file_path}: {str(e)}")


def store_answer(user_id, question_id, prep_session_id, audio_file_name, feedback, correctness, completeness):
    answer = Answer(
        user_id=user_id,
        question_id=question_id,
        prep_session_id=prep_session_id,
        answer_text="parsing audio directly, missing this info",
        audio_file_name=audio_file_name,
        feedback=feedback,
        correctness=correctness,
        completeness=completeness
    )
    db.session.add(answer)
    db.session.commit()
    current_app.logger.info(f"Answer stored in database for user {user_id}, question {question_id}")