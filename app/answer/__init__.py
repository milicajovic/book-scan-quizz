from flask import Blueprint

answer = Blueprint('answer', __name__)

from . import routes