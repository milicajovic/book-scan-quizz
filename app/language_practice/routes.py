import html
import os

from flask import current_app, jsonify, Response, stream_with_context, session, abort
from flask import make_response
from flask import render_template, redirect, url_for
from flask import request
from flask_login import current_user
from flask_login import login_required
from werkzeug.exceptions import NotFound

from google_ai.evaluate_language_audio import evaluate_language_audio
from . import language_practice
from .. import db
from ..models import Question, PrepSession, Answer
from ..models import Quiz
from ..quiz_session.routes import store_answer, extract_feedback_and_scores, validate_input, process_audio_file


# from google_ai import evaluate_text_answer, evaluate_audio_answer


@language_practice.route('/practice/')
@login_required
def practice():
    # Query for the user's last language practice session
    last_session = PrepSession.query.join(Quiz).filter(
        PrepSession.user_id == current_user.id,
        Quiz.type == 'language'
    ).order_by(PrepSession.start_time.desc()).first()

    if not last_session:
        # If no session exists, throw an exception
        abort(404, description="No language practice sessions found for this user.")

    if last_session.status == 'in_progress':
        # If there's an open session, redirect to it
        return redirect(url_for('quiz_session.answer_question', session_id=last_session.id))

    # If the last session is completed, create a new one
    language_quiz = Quiz.query.filter_by(type='language').first()
    if not language_quiz:
        abort(404, description="No language quizzes available.")

    new_session = PrepSession(user_id=current_user.id, quiz_id=language_quiz.id, status='in_progress')
    db.session.add(new_session)
    db.session.commit()

    return redirect(url_for('quiz_session.answer_question', session_id=new_session.id))


@language_practice.route('/start/<quiz_id>')
@login_required
def start(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    existing_session = PrepSession.query.filter_by(
        user_id=current_user.id,
        quiz_id=quiz_id,
        status='in_progress'
    ).first()

    if existing_session:
        return redirect(url_for('language_practice.answer_question', session_id=existing_session.id))

    new_session = PrepSession(user_id=current_user.id, quiz_id=quiz_id, status='in_progress')
    db.session.add(new_session)
    db.session.commit()
    return redirect(url_for('language_practice.answer_question', session_id=new_session.id))


@language_practice.route('/update-mode', methods=['POST'])
@login_required
def update_mode():
    data = request.get_json()
    mode = data.get('mode')
    if mode in ['audio', 'text']:
        session['answer_mode'] = mode
        return jsonify({'status': 'success', 'mode': mode}), 200
    return jsonify({'status': 'error', 'message': 'Invalid mode'}), 400


@language_practice.route('/answer/<session_id>', methods=['GET', 'POST'])
@login_required
def answer_question(session_id):
    prep_session = PrepSession.query.get_or_404(session_id)
    if prep_session.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    answered_count = prep_session.get_distinct_answered_questions_count()
    total_count = prep_session.get_total_quiz_questions_count()

    if total_count == 0:
        raise NotFound("This quiz has no questions. Please contact the administrator.")

    if answered_count >= total_count:
        return redirect(url_for('quiz_session.complete', session_id=session_id))

    current_question = prep_session.get_current_question()
    if not current_question:
        raise NotFound("No question found when one was expected. The quiz may be in an inconsistent state.")

    progress_percentage = (answered_count / total_count) * 100

    # Use the answer_mode from the session, defaulting to 'audio' if not set
    answer_mode = session.get('answer_mode', 'audio')

    # Choose the template based on the answer_mode
    template = 'language_practice/audio.html' if answer_mode == 'audio' else 'language_practice/text.html'

    return render_template(template,
                           question=current_question,
                           session_id=session_id,
                           progress_percentage=progress_percentage,
                           answered_count=answered_count,
                           total_count=total_count,
                           answer_mode=answer_mode)


@language_practice.route('/complete/<session_id>')
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
    answers = Answer.query.join(Question) \
        .filter(Answer.prep_session_id == prep_session.id) \
        .order_by(Question.position, Answer.id) \
        .all()

    response = make_response(render_template('language_practice/complete.html',
                                             session=prep_session,
                                             answers=answers,
                                             answered_questions_count=answered_questions_count,
                                             total_questions_count=total_questions_count))
    return response


def generate_evaluation(question, audio_file_path):
    if not os.path.exists(audio_file_path):
        yield html.escape(f"Error: Audio file not found: {audio_file_path}")
        return

    try:
        for chunk in evaluate_language_audio("English", "German",
                                             question.question_text,
                                             audio_file_path):
            yield chunk
    except Exception as e:
        error_message = f"Error in generate_evaluation: {str(e)}"
        current_app.logger.error(error_message)
        yield html.escape(error_message)


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


@language_practice.route('/evaluate_audio', methods=['POST'])
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


@language_practice.route('/evaluate_text', methods=['POST'])
@login_required
def evaluate_text():
    try:
        text = request.form.get('text')
        question_id = request.form.get('question_id')
        session_id = request.form.get('session_id')

        if not text or not question_id or not session_id:
            return jsonify({'error': 'Missing required data'}), 400

        question = Question.query.get(question_id)
        if not question:
            return jsonify({'error': 'Question not found'}), 404

        prep_session = PrepSession.query.get(session_id)
        if not prep_session or prep_session.user_id != current_user.id:
            return jsonify({'error': 'Invalid session'}), 403

        # evaluation_result = evaluate_text_answer(question.question_text, question.answer, text)
        raise NotImplemented("Not implemented yet")
        # Extract feedback and scores
        feedback, correctness, completeness = extract_feedback_and_scores(evaluation_result)

        # Store the answer using the existing store_answer function
        store_answer(
            user_id=current_user.id,
            question_id=question_id,
            prep_session_id=session_id,
            audio_file_name="not-used",
            feedback=feedback,
            correctness=correctness,
            completeness=completeness,
            answer_text=text  # Add this new parameter
        )

        return evaluation_result

    except Exception as e:
        current_app.logger.error(f"Error in evaluate_text: {str(e)}")
        return jsonify({'error': f'An error occurred while evaluating the answer {str(e)}'}), 500
