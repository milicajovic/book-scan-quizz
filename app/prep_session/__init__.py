from flask import Blueprint

prep_session = Blueprint('prep_session', __name__)

from . import routes