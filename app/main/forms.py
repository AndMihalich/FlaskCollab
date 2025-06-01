from wtforms import Form, StringField, PasswordField, SubmitField, validators
from flask_wtf import FlaskForm
from wtforms.validators import ValidationError, DataRequired, Length, Email, Regexp
from ..models import User, Role
from wtforms import TextAreaField, BooleanField, SelectField

class SearchForm(FlaskForm):
    query = StringField('Search', validators=[validators.DataRequired(),

                                              validators.Length(min=4, max=20)])
    submit = SubmitField('Search')

    def validate_query(self, field):
        if not User.query.filter_by(username=field.data).first():
            return ValidationError('User does not exist')

class EditProfileForm(FlaskForm):
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
    about_me = TextAreaField('About me', validators=[Length(0, 300)])
    submit = SubmitField('Save changes')
    
    


class EditProfileAdminForm(EditProfileForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    role = SelectField('Role', coerce=int)
    submit = SubmitField('Save changes')

    def __init__(self, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]

    def validate_email(self, field):
        if not User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered')

    def validate_username(self, field):
        if not User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already exists')

