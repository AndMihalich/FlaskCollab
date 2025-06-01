from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, StringField
from wtforms.validators import DataRequired, Length

class MessageForm(FlaskForm):
    content = StringField('Message', validators=[
        DataRequired(),
        Length(min=1, max=1000, message='The message is too long')
    ])
    submit = SubmitField('Send')


class StartChatForm(FlaskForm):
    username = StringField('Enter Username', validators=[DataRequired(), Length(min=4, max=20)])
    submit = SubmitField('Start Chat')