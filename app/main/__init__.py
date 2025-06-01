from flask import Blueprint

blue_main = Blueprint('main', __name__)

from . import views, errors
