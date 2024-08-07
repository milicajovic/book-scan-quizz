from flask import redirect, url_for, flash, session, request
from flask_login import login_user, logout_user, current_user

from . import auth
from ..models import User
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
    try:
        token = oauth.google.authorize_access_token()
        user_info = token.get('userinfo')

        if user_info:
            user = User.get_or_create(
                email=user_info['email'],
                first_name=user_info.get('given_name'),
                last_name=user_info.get('family_name'),
                picture=user_info.get('picture')
            )
            login_user(user)
            session['user'] = user.to_dict()  # Store all user info in session
            flash('Logged in successfully.', 'success')
            # Redirect to the next URL if it exists, otherwise go to home
            next_url = session.pop('next', None)

            if next_url:
                return redirect(next_url)
            return redirect(url_for('main.home'))
        else:
            flash('Failed to get user info from Google.', 'danger')

        return redirect(url_for('main.home'))
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('main.home'))
