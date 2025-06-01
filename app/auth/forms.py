from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Regexp
from ..models import User

class LoginForm(FlaskForm):
    email = StringField('Email or username', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[
            DataRequired(),
            Length(4, 20, message='Username must be between 4 and 20 characters.'),
            Regexp(r'^(?!.*__)(?!.*_$)[a-z][a-z0-9_]{2,19}(?<!_)$', 0,
                   'Usernames must have only lowercase letters, numbers, underscores (one in row maximum).')])
    first_name = StringField('First name', validators=[
        DataRequired(), Length(2, 64), Regexp(r"(?i)^[a-zà-ÿ]+(?:[-'][a-zà-ÿ]+)*$", 0,
                   'First name must contain only letters, hyphens or apostrophes.')])
    last_name = StringField('Last name', validators=[
        DataRequired(), Length(2, 64), Regexp(r"(?i)^[a-zà-ÿ]+(?:[-'][a-zà-ÿ]+)*$", 0,
                   'Last name must contain only letters, hyphens or apostrophes.')])
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(6, 128)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')