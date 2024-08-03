from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, MultipleFileField, SelectField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed, FileRequired
from ..models.models import QuizType

class CreateQuizForm(FlaskForm):
    title = StringField('Quiz Title', validators=[DataRequired()])
    language = StringField('Quiz Language')
    type = SelectField('Quiz Type', choices=[(qt.name, qt.value) for qt in QuizType], validators=[DataRequired()])
    images = MultipleFileField('Upload Images', validators=[
       # FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')
    ])
    submit = SubmitField('Create Quiz')

class EditQuizForm(FlaskForm):
    title = StringField('Quiz Title', validators=[DataRequired()])
    lng = StringField('Quiz Language')
    type = SelectField('Quiz Type', choices=[(qt.name, qt.value) for qt in QuizType], validators=[DataRequired()])
    images = MultipleFileField('Upload Additional Images', validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')
    ])
    submit = SubmitField('Update Quiz')

class QuestionForm(FlaskForm):
    question_text = StringField('Question', validators=[DataRequired()])
    answer = StringField('Answer', validators=[DataRequired()])
    difficulty_level = SelectField('Difficulty Level',
                                   choices=[('easy', 'Easy'),
                                            ('medium', 'Medium'),
                                            ('hard', 'Hard')],
                                   validators=[DataRequired()])
    submit = SubmitField('Save Question')

