from flask import Blueprint

quiz_session = Blueprint('quiz_session', __name__)

from . import routes