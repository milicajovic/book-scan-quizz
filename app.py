from flask import Flask, render_template, redirect, url_for, session, request
from authlib.integrations.flask_client import OAuth
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)
oauth = OAuth(app)

google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)

@app.route('/')
def home():
    return render_template('home.html', active_page='home')

@app.route('/about')
def about():
    return render_template('about.html', active_page='about')

@app.route('/services')
def services():
    return render_template('services.html', active_page='services')

@app.route('/contact')
def contact():
    return render_template('contact.html', active_page='contact')

@app.route('/login')
def login():
    redirect_uri = url_for('authorized', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/logout')
def logout():
    session.pop('google_token', None)
    session.pop('user_email', None)
    return redirect(url_for('home'))

@app.route('/login/authorized')
def authorized():
    token = google.authorize_access_token()
    user_info = token.get('userinfo')
    if user_info:
        session['google_token'] = token
        session['user_email'] = user_info['email']
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)