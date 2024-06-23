from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, email):
        self.id = id
        self.email = email

    @staticmethod
    def get(user_id):
        # This method is used by Flask-Login to reload the user object from the user ID stored in the session
        return User(id=user_id, email=None)