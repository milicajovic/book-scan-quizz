from flask import Blueprint

language_practice = Blueprint('language_practice', __name__)

from . import routes