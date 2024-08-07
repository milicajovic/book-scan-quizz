from flask import render_template, request, redirect, url_for
from .extensions import login_manager
from .models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@login_manager.unauthorized_handler
def unauthorized():
    if request.blueprint == 'api':
        return {'error': 'Unauthorized'}, 401
    else:
        # Store the current URL as the next parameter
        next_url = request.url
        login_url = url_for('auth.login', next=next_url)
        #return redirect(login_url)
        return render_template('errors/403.html', login_url=login_url), 403