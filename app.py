from flask import Flask, render_template, redirect, url_for, session, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth
from authlib.integrations.base_client.errors import OAuthError
from config import config
import os
from werkzeug.utils import secure_filename

db = SQLAlchemy()
oauth = OAuth()

def home():
    return render_template('home.html', active_page='home')

def about():
    return render_template('about.html', active_page='about')

def quizz():
    return render_template('quizz.html', active_page='services')

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
    try:
        google = oauth.create_client('google')
        token = google.authorize_access_token()
        user_info = token.get('userinfo')
        if user_info:
            session['google_token'] = token
            session['user_email'] = user_info['email']
            flash('Successfully logged in!', 'success')
        return redirect(url_for('home'))
    except OAuthError as e:
        flash('Failed to log in. Access was denied.', 'danger')
        return redirect(url_for('home'))


def evaluate_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']

    if audio_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if audio_file:
        filename = secure_filename(audio_file.filename)

        # Ensure the upload folder exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        audio_file.save(filepath)

        # Here you would typically process the audio file
        # For now, we'll just return a success message with the file path
        return jsonify({
            'result': 'Audio file saved successfully',
            'filepath': filepath
        })


def create_app(config_name=None):
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = 'audio_uploads'
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
    app.add_url_rule('/quizz', 'quizz', quizz)
    app.add_url_rule('/contact', 'contact', contact)
    app.add_url_rule('/login', 'login', login)
    app.add_url_rule('/logout', 'logout', logout)
    app.add_url_rule('/login/authorized', 'authorized', authorized)
    app.add_url_rule('/evaluate_audio', 'evaluate_audio', evaluate_audio, methods=['POST'])

    return app

app = create_app()

if __name__ == '__main__':
    app.run()