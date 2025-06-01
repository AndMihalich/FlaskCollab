from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField
from wtforms.validators import DataRequired
from flask_wtf.file import FileRequired, FileAllowed 

class CreateSubjectForm(FlaskForm):
    name = StringField('Subject Name', validators=[DataRequired()])
    submit = SubmitField('Create Subject')

class JoinSubjectForm(FlaskForm):
    code = StringField('Subject Code', validators=[DataRequired()])
    submit = SubmitField('Join Subject')

class PostMaterialForm(FlaskForm):
    title = StringField('Post Title', validators=[DataRequired()])
    file = FileField('Upload Material', validators=[DataRequired()])
    submit = SubmitField('Post')
