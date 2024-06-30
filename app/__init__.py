import logging
import os

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask_migrate import Migrate
from config import config
from .utils import init_oauth, oauth

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

# Create metadata with naming convention
metadata = MetaData(naming_convention=convention)

# Create db with the metadata
db = SQLAlchemy(metadata=metadata)
migrate = Migrate()

login_manager = LoginManager()

def create_app(config_name=None):
    app = Flask(__name__)

    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'default')

    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    migrate.init_app(app, db)

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

    from .answer import answer as quiz_blueprint
    app.register_blueprint(quiz_blueprint, url_prefix='/answer')

    from .quiz import quiz as quiz_blueprint
    app.register_blueprint(quiz_blueprint, url_prefix='/quiz')

    # Import and register the init-db command
    from .cli import init_db_command
    app.cli.add_command(init_db_command)

    return app
