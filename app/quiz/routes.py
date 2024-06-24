from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from . import quiz
from .forms import CreateQuizForm, EditQuestionForm
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