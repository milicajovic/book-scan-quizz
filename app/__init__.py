import logging
import os

from flask import Flask
from config import config
from .extensions import init_extensions, db
from .utils import init_oauth
from .error_handlers import register_error_handlers

def create_app(config_name=None):
    app = Flask(__name__)

    print(f"Initial configuration: {config_name}")

    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'default')

    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Print the current configuration
    print(f"Used configuration: {config_name}")

    app.logger.info(f"Application started with configuration: {config_name}")

    init_extensions(app)
    init_oauth(app)

    if app.config['SQLALCHEMY_ECHO']:
        # Set up SQLAlchemy query logging
        logging.basicConfig()
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    # Import models to ensure they are registered with SQLAlchemy
    from .models import User, Quiz, Question, Answer, PageScan, PrepSession

    # Import auth_helpers here to avoid circular imports
    from . import auth_helpers

    # Register blueprints
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .quiz import quiz as quiz_blueprint
    app.register_blueprint(quiz_blueprint, url_prefix='/quiz')

    from .quiz_session import quiz_session as quiz_session_blueprint
    app.register_blueprint(quiz_session_blueprint, url_prefix='/quiz-session')

    from .language_practice import language_practice as language_practice_blueprint
    app.register_blueprint(language_practice_blueprint, url_prefix='/language-practice')

    # Import and register the init-db command
    from .cli import init_db_command
    app.cli.add_command(init_db_command)

    # Register error handlers
    register_error_handlers(app)

    return app