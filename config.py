import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_required_env_var(var_name):
    value = os.environ.get(var_name)
    if not value:
        raise ValueError(f"Missing required environment variable: {var_name}")
    return value
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    GOOGLE_CLIENT_ID = get_required_env_var('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = get_required_env_var('GOOGLE_CLIENT_SECRET')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'audio_uploads'
    GEMINI_API_KEY = get_required_env_var('GEMINI_API_KEY')
    SQLALCHEMY_ECHO = False  # Default to False, enable per environment as needed

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'dev.sqlite')
    SQLALCHEMY_ECHO = False  # Enable SQL query logging for development


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = get_required_env_var('DB_URL')
    SQLALCHEMY_ECHO = False  # Enable SQL query logging for testing


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = get_required_env_var('DB_URL')

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # log to syslog
        import logging
        from logging.handlers import SysLogHandler
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}