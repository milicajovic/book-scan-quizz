from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, email, first_name=None, last_name=None, picture=None):
        self.id = id
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.picture = picture

    @staticmethod
    def get(user_id):
        # This method is used by Flask-Login to reload the user object from the user ID stored in the session
        # In a real application, you'd fetch this information from a database or session
        return User(id=user_id, email=None)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'picture': self.picture
        }

    @staticmethod
    def from_dict(data):
        return User(
            id=data.get('id'),
            email=data.get('email'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            picture=data.get('picture')
        )