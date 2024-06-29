from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, MultipleFileField, IntegerField
from wtforms.validators import DataRequired, NumberRange
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
    difficulty_level = IntegerField('Difficulty Level', validators=[NumberRange(min=1, max=10)])
    submit = SubmitField('Save Question')