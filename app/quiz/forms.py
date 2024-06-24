from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, MultipleFileField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed

class CreateQuizForm(FlaskForm):
    title = StringField('Quiz Title', validators=[DataRequired()])
    images = MultipleFileField('Upload Images', validators=[
        FileAllowed(['jpg', 'png'], 'Images only!')
    ])
    submit = SubmitField('Create Quiz')

class EditQuestionForm(FlaskForm):
    # Add fields for editing questions
    pass