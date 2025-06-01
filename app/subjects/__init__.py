from flask import Blueprint

subjects = Blueprint('subj', __name__)

from . import views