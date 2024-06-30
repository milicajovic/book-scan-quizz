from flask import render_template, redirect, url_for, request, jsonify, current_app
from flask_login import login_required, current_user
from . import prep_session
from app import db
from ..models import PrepSession, Quiz, Question, Answer
from google_ai import transcribe_audio
import os
from werkzeug.utils import secure_filename

from flask import flash


@prep_session.route('/start/<quiz_id>')
@login_required
def start(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)

    # Check if user already has an in-progress or completed session for this quiz
    existing_session = PrepSession.query.filter_by(
        user_id=current_user.id,
        quiz_id=quiz_id
    ).filter(PrepSession.status.in_(['in_progress', 'completed'])).first()

    if existing_session:
        if existing_session.status == 'in_progress':
            flash('You already have an in-progress session for this quiz. Continuing from where you left off.', 'info')
            return redirect(url_for('prep_session.answer_question', session_id=existing_session.id))
        else:
            flash('You have already completed this quiz. Starting a new session.', 'info')

    new_session = PrepSession(user_id=current_user.id, quiz_id=quiz_id, status='in_progress')
    db.session.add(new_session)
    db.session.commit()
    return redirect(url_for('prep_session.answer_question', session_id=new_session.id))


@prep_session.route('/answer/<session_id>', methods=['GET', 'POST'])
@login_required
def answer_question(session_id):
    prep_session = PrepSession.query.get_or_404(session_id)
    if prep_session.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    if request.method == 'POST':
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400

        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if audio_file:
            filename = secure_filename(audio_file.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            audio_file.save(filepath)

            transcription = transcribe_audio(filepath)

            # Here you would process the transcription and save the answer
            # For now, we'll just save the transcription as the answer
            current_question = prep_session.get_current_question()
            new_answer = Answer(
                user_id=current_user.id,
                question_id=current_question.id,
                prep_session_id=prep_session.id,
                answer_text=transcription,
                audio_file_name=filename
            )
            db.session.add(new_answer)
            db.session.commit()

            return jsonify({'success': True, 'transcription': transcription})

    current_question = prep_session.get_current_question()
    if not current_question:
        prep_session.status = 'completed'
        db.session.commit()
        return redirect(url_for('prep_session.complete', session_id=session_id))

    return render_template('prep_session/answer_question.html', question=current_question, session_id=session_id)


@prep_session.route('/complete/<session_id>')
@login_required
def complete(session_id):
    prep_session = PrepSession.query.get_or_404(session_id)
    if prep_session.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    # Here you would calculate the score and provide feedback
    # For now, we'll just mark the session as completed
    prep_session.status = 'completed'
    db.session.commit()

    return render_template('prep_session/complete.html', session=prep_session)