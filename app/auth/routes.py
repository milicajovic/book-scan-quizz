from flask import redirect, url_for, flash, session
from flask_login import login_user, logout_user, current_user
from . import auth
from ..models import User
from .. import db
from ..utils import oauth

@auth.route('/login')
def login():
    return oauth.google.authorize_redirect(url_for('auth.authorized', _external=True))

@auth.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
    session.clear()  # This clears all session data
    flash('You have been logged out.', 'danger')
    return redirect(url_for('main.home'))

@auth.route('/login/authorized')
def authorized():
    token = oauth.google.authorize_access_token()
    user_info = token.get('userinfo')
    print(f" token:{user_info} info:{user_info}" )
    if user_info:
        user = User(id=user_info['sub'], email=user_info['email'])
        login_user(user)
        session['user_email'] = user_info['email']  # Store email in session
        flash('Logged in successfully.', 'danger')
        print("user loged in" + session['user_email'])
    return redirect(url_for('main.home'))