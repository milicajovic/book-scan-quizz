from flask import render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from . import quiz
from .forms import CreateQuizForm, EditQuizForm, QuestionForm
from .. import db
from ..models import Quiz, Question, PageScan
from google_ai import generate_questions  # Updated import statement
from flask import jsonify


@quiz.route('/')
@login_required
def index():
    user_quizzes = Quiz.query.filter_by(user_owner_id=current_user.id).all()
    return render_template('quiz/index.html', quizzes=user_quizzes)


@quiz.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = CreateQuizForm()
    if form.validate_on_submit():
        try:
            quiz = Quiz(title=form.title.data, user_owner_id=current_user.id)
            db.session.add(quiz)
            db.session.flush()  # To get the quiz id

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

            # Generate questions
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

            flash('Quiz created successfully!', 'success')
            return redirect(url_for('quiz.edit', quiz_id=quiz.id))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating quiz: {str(e)}")
            flash(f'An error occurred while creating {str(e)}', 'error')

    return render_template('quiz/create.html', form=form)

@quiz.route('/<quiz_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if quiz.user_owner_id != current_user.id:
        abort(403)

    form = EditQuizForm(obj=quiz)
    if form.validate_on_submit():
        quiz.title = form.title.data

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
