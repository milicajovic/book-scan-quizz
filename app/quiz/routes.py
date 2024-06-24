from flask import render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_required, current_user
from . import quiz
from .forms import CreateQuizForm, QuestionForm, EditQuestionForm
from .. import db
from ..models import Quiz, Question, PageScan
from werkzeug.utils import secure_filename
import os


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
        quiz = Quiz(title=form.title.data, user_owner_id=current_user.id)
        db.session.add(quiz)
        db.session.flush()  # To get the quiz id

        for image in request.files.getlist('images'):
            if image:
                filename = secure_filename(image.filename)
                image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                page_scan = PageScan(quiz_id=quiz.id, file_name=filename)
                db.session.add(page_scan)

        db.session.commit()
        flash('Quiz created successfully!', 'success')
        return redirect(url_for('quiz.index'))
    return render_template('quiz/create.html', form=form)


@quiz.route('/<quiz_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if quiz.user_owner_id != current_user.id:
        flash('You do not have permission to edit this quiz.', 'danger')
        return redirect(url_for('quiz.index'))

    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    form = EditQuestionForm()

    if form.validate_on_submit():
        # Logic to save edited questions
        pass

    return render_template('quiz/edit.html', quiz=quiz, questions=questions, form=form)


@quiz.route('/<quiz_id>/answer')
@login_required
def answer(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    return render_template('quiz/answer.html', quiz=quiz, questions=questions)


@quiz.route('/<quiz_id>/add_question', methods=['GET', 'POST'])
@login_required
def add_question(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if quiz.user_owner_id != current_user.id:
        abort(403)

    form = QuestionForm()
    if form.validate_on_submit():
        question = Question(
            quiz_id=quiz_id,
            question_text=form.question_text.data,
            answer=form.answer.data,
            difficulty_level=form.difficulty_level.data
        )
        db.session.add(question)
        db.session.commit()
        flash('Question added successfully!', 'success')
        return redirect(url_for('quiz.edit', quiz_id=quiz_id))

    return render_template('quiz/add_question.html', form=form, quiz=quiz)


@quiz.route('/<quiz_id>/edit_question/<question_id>', methods=['GET', 'POST'])
@login_required
def edit_question(quiz_id, question_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    question = Question.query.get_or_404(question_id)
    if quiz.user_owner_id != current_user.id or question.quiz_id != quiz_id:
        abort(403)

    form = QuestionForm(obj=question)
    if form.validate_on_submit():
        form.populate_obj(question)
        db.session.commit()
        flash('Question updated successfully!', 'success')
        return redirect(url_for('quiz.edit', quiz_id=quiz_id))

    return render_template('quiz/edit_question.html', form=form, quiz=quiz, question=question)


@quiz.route('/<quiz_id>/delete_question/<question_id>', methods=['POST'])
@login_required
def delete_question(quiz_id, question_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    question = Question.query.get_or_404(question_id)
    if quiz.user_owner_id != current_user.id or question.quiz_id != quiz_id:
        abort(403)

    db.session.delete(question)
    db.session.commit()
    flash('Question deleted successfully!', 'success')
    return redirect(url_for('quiz.edit', quiz_id=quiz_id))