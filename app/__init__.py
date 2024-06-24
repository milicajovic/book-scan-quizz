from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config
from .utils import init_oauth, oauth
import os
import logging

db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_name=None):
    app = Flask(__name__)

    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'default')

    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)

    if app.config['SQLALCHEMY_ECHO']:
        # Set up SQLAlchemy query logging
        logging.basicConfig()
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    login_manager.init_app(app)
    init_oauth(app)

    from .models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)


    # Register blueprints
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .quiz import quiz as quiz_blueprint
    app.register_blueprint(quiz_blueprint, url_prefix='/quiz')

    # Import and register the init-db command
    from .cli import init_db_command
    app.cli.add_command(init_db_command)

    return app