from flask import Flask, render_template, redirect, url_for, session, request
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth
from config import config
import os

db = SQLAlchemy()
oauth = OAuth()

def home():
    return render_template('home.html', active_page='home')

def about():
    return render_template('about.html', active_page='about')

def services():
    return render_template('services.html', active_page='services')

def contact():
    return render_template('contact.html', active_page='contact')

def login():
    google = oauth.create_client('google')
    redirect_uri = url_for('authorized', _external=True)
    return google.authorize_redirect(redirect_uri)

def logout():
    session.pop('google_token', None)
    session.pop('user_email', None)
    return redirect(url_for('home'))

def authorized():
    google = oauth.create_client('google')
    token = google.authorize_access_token()
    user_info = token.get('userinfo')
    if user_info:
        session['google_token'] = token
        session['user_email'] = user_info['email']
    return redirect(url_for('home'))

def create_app(config_name=None):
    app = Flask(__name__)

    # Use the specified config_name, or default to the FLASK_CONFIG environment variable, or use 'default'
    config_name = config_name or os.getenv('FLASK_CONFIG', 'default')
    app.config.from_object(config[config_name])

    db.init_app(app)
    oauth.init_app(app)

    oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'},
    )

    app.add_url_rule('/', 'home', home)
    app.add_url_rule('/about', 'about', about)
    app.add_url_rule('/services', 'services', services)
    app.add_url_rule('/contact', 'contact', contact)
    app.add_url_rule('/login', 'login', login)
    app.add_url_rule('/logout', 'logout', logout)
    app.add_url_rule('/login/authorized', 'authorized', authorized)

    return app

# This allows both "flask run" to work and "python app.py" to work
app = create_app()

if __name__ == '__main__':
    app.run()