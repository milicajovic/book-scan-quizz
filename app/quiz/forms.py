from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, MultipleFileField, SelectField, IntegerField
from wtforms.validators import DataRequired, Optional
from flask_wtf.file import FileAllowed, FileRequired
from ..models.models import QuizType

def get_language_choices():
    return [
        ('en', 'English'),
        ('de', 'German'),
        ('fr', 'French'),
        ('hr', 'Croatian'),
        ('sr', 'Serbian')
    ]

class CreateQuizForm(FlaskForm):
    title = StringField('Quiz Title', validators=[Optional()])  # Changed from DataRequired() to Optional()
    lng = SelectField('Quiz Language', choices=get_language_choices(), validators=[DataRequired()])
    target_lng = SelectField('Target Language', choices=get_language_choices(), validators=[Optional()])
    type = SelectField('Quiz Type', choices=[(qt.name, qt.value) for qt in QuizType], validators=[DataRequired()])
    images = MultipleFileField('Upload Images', validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')
    ])
    submit = SubmitField('Create Quiz')


class EditQuizForm(FlaskForm):
    title = StringField('Quiz Title', validators=[DataRequired()])
    lng = SelectField('Quiz Language', choices=get_language_choices(), validators=[DataRequired()])
    target_lng = SelectField('Target Language', choices=get_language_choices(), validators=[Optional()])
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
    position = IntegerField('Position', validators=[Optional()])

    submit = SubmitField('Save Question')