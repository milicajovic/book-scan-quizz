import json
import os

from flask import render_template, redirect, url_for, request, jsonify, current_app, Response, stream_with_context
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from google_ai import transcribe_audio
from google_ai.audio_answer_evaluator import evaluate_audio_answer
from . import quiz_session
from .. import db
from ..models import PrepSession, Quiz, Question, Answer


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


def generate_evaluation(question, prep_session, audio_path, filename):
    evaluation_result = ''
    try:
        for chunk in evaluate_audio_answer(question.question_text, question.answer, audio_path):
            evaluation_result += chunk
            yield chunk

        correctness, completeness = process_evaluation_result(evaluation_result)

        store_answer(current_user.id, question.id, prep_session.id, audio_path, filename,
                     evaluation_result, correctness, completeness)

        response_data = prepare_response_data(prep_session)
        yield '\n' + json.dumps(response_data)

    finally:
        os.remove(audio_path)

def save_audio_file(audio_file):
    filename = secure_filename(audio_file.filename)
    audio_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    audio_file.save(audio_path)
    return audio_path, filename

def process_evaluation_result(evaluation_result):
    parts = evaluation_result.split('####')
    correctness = completeness = 0
    if len(parts) > 1:
        scores = parts[1].strip().split('\n')
        correctness = float(scores[0].split(':')[1].strip())
        completeness = float(scores[1].split(':')[1].strip())
    return correctness, completeness

def store_answer(user_id, question_id, session_id, audio_path, filename, evaluation_result, correctness, completeness):
    answer = Answer(
        user_id=user_id,
        question_id=question_id,
        prep_session_id=session_id,
        answer_text=transcribe_audio(audio_path),
        audio_file_name=filename,
        feedback=evaluation_result,
        correctness=correctness,
        completeness=completeness
    )
    db.session.add(answer)
    db.session.commit()

def prepare_response_data(prep_session):
    next_question = prep_session.get_current_question()
    return {
        'next_question': next_question.id if next_question else None,
        'session_completed': next_question is None
    }


def process_audio_response(audio_file, question, prep_session):
    audio_path, filename = save_audio_file(audio_file)
    evaluation_result = evaluate_audio_answer(question.question_text, question.answer, audio_path)
    transcription = transcribe_audio(audio_path)

    answer = Answer(
        user_id=current_user.id,
        question_id=question.id,
        prep_session_id=prep_session.id,
        answer_text=transcription,
        audio_file_name=filename,
        feedback=evaluation_result
    )
    db.session.add(answer)
    db.session.commit()

    os.remove(audio_path)
    return evaluation_result


def get_next_action(prep_session):
    next_question = prep_session.get_current_question()
    if next_question:
        return {'next_question': True}
    else:
        prep_session.status = 'completed'
        db.session.commit()
        return {'session_completed': True}


@quiz_session.route('/evaluate_audio', methods=['POST'])
@login_required
def evaluate_audio():
    try:
        audio_file = request.files.get('audio')
        question_id = request.form.get('question_id')
        session_id = request.form.get('session_id')

        if not audio_file or not question_id or not session_id:
            return jsonify({'error': 'Missing required data'}), 400

        question = Question.query.get(question_id)
        prep_session = PrepSession.query.get(session_id)

        if not question or not prep_session:
            return jsonify({'error': 'Question or session not found'}), 404

        evaluation_result = process_audio_response(audio_file, question, prep_session)
        next_action = get_next_action(prep_session)

        return jsonify({
            'status': 'success',
            'message': evaluation_result,
            **next_action
        })

    except Exception as e:
        current_app.logger.error(f"Error in evaluate_audio: {str(e)}")
        return jsonify({'error': f'An error occurred while processing the audio: {str(e)}'}), 500