from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, MultipleFileField, SelectField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed, FileRequired

class CreateQuizForm(FlaskForm):
    title = StringField('Quiz Title', validators=[DataRequired()])
    images = MultipleFileField('Upload Images', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')
    ])
    submit = SubmitField('Create Quiz')

class EditQuizForm(FlaskForm):
    title = StringField('Quiz Title', validators=[DataRequired()])
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