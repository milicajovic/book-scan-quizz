from flask import render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from . import quiz
from .forms import CreateQuizForm, EditQuizForm, QuestionForm
from .. import db
from ..models import Quiz, Question, PageScan, PrepSession
from google_ai import generate_questions  # Updated import statement
from flask import jsonify


@quiz.route('/')
@login_required
def index():
    user_quizzes = Quiz.query.filter_by(user_owner_id=current_user.id).all()
    return render_template('quiz/index.html', quizzes=user_quizzes)


@quiz.route('/dispatch_session/<string:session_id>')
@login_required
def dispatch_session(session_id):
    prep_session = PrepSession.query.get_or_404(session_id)

    # Check if the user owns this session
    if prep_session.user_id != current_user.id:
        abort(403)  # Forbidden if the user doesn't own the session
    # Check the quiz type
    if prep_session.quiz.type.lower() == 'language':
        return redirect(url_for('language_practice.answer_question', session_id=session_id))
    else:
        return redirect(url_for('quiz_session.answer_question', session_id=session_id))


@quiz.route('/dispatch/<string:quiz_id>')
def dispatch(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if quiz.type.lower() == 'language':
        return redirect(url_for('language_practice.start', quiz_id=quiz_id))
    else:
        return redirect(url_for('quiz_session.start', quiz_id=quiz_id))




@quiz.route('/my-sessions')
@login_required
def my_sessions():
    # Fetch all prep sessions for the current user
    prep_sessions = PrepSession.query.filter_by(user_id=current_user.id).order_by(PrepSession.start_time.desc()).all()

    # Prepare data for the template
    sessions_data = []
    for session in prep_sessions:
        total_questions = session.get_total_quiz_questions_count()
        answered_questions = session.get_distinct_answered_questions_count()
        progress_percentage = (answered_questions / total_questions) * 100 if total_questions > 0 else 0

        sessions_data.append({
            'id': session.id,
            'quiz_title': session.quiz.title,
            'quiz_id': session.quiz_id,  # Add this line
            'start_time': session.start_time,
            'status': session.status,
            'progress': {
                'answered': answered_questions,
                'total': total_questions,
                'percentage': progress_percentage
            }
        })

    return render_template('quiz/my_sessions.html', sessions=sessions_data)


@quiz.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = CreateQuizForm()
    if form.validate_on_submit():
        try:
            quiz = save_quiz(form.title.data, form.language.data, form.type.data)
            uploaded_images = process_uploaded_images(form.images.data, quiz.id)
            generate_and_save_questions(uploaded_images, quiz.id)

            db.session.commit()
            flash('Quiz created successfully!', 'success')
            return redirect(url_for('quiz.edit', quiz_id=quiz.id))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating quiz: {str(e)}")
            flash(f'An error occurred while creating the quiz: {str(e)}', 'error')

    return render_template('quiz/create.html', form=form)

def save_quiz(title, language, quiz_type):
    try:
        quiz = Quiz(title=title, language=language, type=quiz_type, user_owner_id=current_user.id)
        db.session.add(quiz)
        db.session.flush()  # To get the quiz id
        return quiz
    except Exception as e:
        current_app.logger.error(f"Error saving quiz: {str(e)}")
        raise

@quiz.route('/<quiz_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if quiz.user_owner_id != current_user.id:
        abort(403)

    form = EditQuizForm(obj=quiz)
    if form.validate_on_submit():
        quiz.title = form.title.data
        quiz.language = form.language.data
        quiz.type = form.type.data

        uploaded_images = []
        for image in form.images.data:
            if image:
                filename = secure_filename(image.filename)
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                image.save(filepath)
                page_scan = PageScan(quiz_id=quiz.id, file_name=filename)
                db.session.add(page_scan)
                uploaded_images.append(filepath)

        db.session.commit()

        # Generate questions for new images
        if uploaded_images:
            questions = generate_questions(uploaded_images)
            for q in questions:
                question = Question(
                    quiz_id=quiz.id,
                    question_text=q['question'],
                    answer=q['answer'],
                    difficulty_level=q['difficulty_level']
                )
                db.session.add(question)
            db.session.commit()

        flash('Quiz updated successfully!', 'success')
        return redirect(url_for('quiz.edit', quiz_id=quiz.id))

    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    return render_template('quiz/edit.html', form=form, quiz=quiz, questions=questions)


@quiz.route('/<quiz_id>/add_empty_question', methods=['POST'])
@login_required
def add_empty_question(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if quiz.user_owner_id != current_user.id:
        abort(403)

    new_question = Question(
        quiz_id=quiz.id,
        question_text="",
        answer="",
        difficulty_level="medium"  # Default difficulty
    )
    db.session.add(new_question)
    db.session.commit()

    return jsonify({'success': True, 'question_id': new_question.id})


def process_uploaded_images(images, quiz_id):
    """
    Process uploaded images and create PageScan objects.

    Args:
        images (list): List of uploaded image files from the form.
        quiz_id (str): The ID of the quiz these images belong to.

    Returns:
        list: A list of file paths for the uploaded images.

    Raises:
        Exception: If there's an error processing the images or saving to the database.
    """
    try:
        uploaded_images = []
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)

        for image in images:
            if image:
                filename = secure_filename(image.filename)
                filepath = os.path.join(upload_folder, filename)
                image.save(filepath)

                page_scan = PageScan(quiz_id=quiz_id, file_name=filename)
                db.session.add(page_scan)

                uploaded_images.append(filepath)

        return uploaded_images
    except Exception as e:
        current_app.logger.error(f"Error processing uploaded images: {str(e)}")
        raise
def generate_and_save_questions(uploaded_images, quiz_id):
    """
    Generate questions from uploaded images and save them to the database.

    Args:
        uploaded_images (list): List of file paths for the uploaded images.
        quiz_id (str): The ID of the quiz these questions belong to.

    Raises:
        Exception: If there's an error generating questions or saving to the database.
    """
    try:
        if uploaded_images:
            questions = generate_questions(uploaded_images)
            for q in questions:
                question = Question(
                    quiz_id=quiz_id,
                    question_text=q['question'],
                    answer=q['answer'],
                    difficulty_level=q['difficulty_level']
                )
                db.session.add(question)
    except Exception as e:
        current_app.logger.error(f"Error generating and saving questions: {str(e)}")
        raise


@quiz.route('/<quiz_id>/delete_question/<question_id>', methods=['POST'])
@login_required
def delete_question(quiz_id, question_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if quiz.user_owner_id != current_user.id:
        abort(403)

    question = Question.query.get_or_404(question_id)
    if question.quiz_id != quiz.id:
        abort(400)

    db.session.delete(question)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Question deleted successfully!'})

# @quiz.route('/<quiz_id>/answer', methods=['GET', 'POST'])
# @login_required
# def answer(quiz_id):
#     quiz = Quiz.query.get_or_404(quiz_id)
#     questions = Question.query.filter_by(quiz_id=quiz_id).all()
#
#     if request.method == 'POST':
#         # Process answers here
#         # This is a placeholder for answer processing logic
#         flash('Answers submitted successfully!', 'success')
#         return redirect(url_for('quiz.index'))
#
#     return render_template('quiz/answer.html', quiz=quiz, questions=questions)


# Add this new route to your existing routes.py file

@quiz.route('/<quiz_id>/edit_question/<question_id>', methods=['GET', 'POST'])
@login_required
def edit_question(quiz_id, question_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    question = Question.query.get_or_404(question_id)

    if quiz.user_owner_id != current_user.id or question.quiz_id != quiz.id:
        abort(403)

    form = QuestionForm(obj=question)

    if form.validate_on_submit():
        question.question_text = form.question_text.data
        question.answer = form.answer.data
        question.difficulty_level = form.difficulty_level.data
        db.session.commit()
        flash('Question updated successfully!', 'success')
        return redirect(url_for('quiz.edit', quiz_id=quiz_id))

    return render_template('quiz/edit_question.html', form=form, quiz=quiz, question=question)
