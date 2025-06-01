from flask import Blueprint

messenger = Blueprint('mess', __name__)

from . import views, errors