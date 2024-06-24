from flask_login import UserMixin
from sqlalchemy import Column, String
from .. import db
import uuid


class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name = Column(String(255))
    last_name = Column(String(255))
    email = Column(String(255), unique=True)
    picture = Column(String(255))

    def __init__(self, email, first_name=None, last_name=None, picture=None):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.picture = picture

    @staticmethod
    def get(user_id):
        return User.query.get(user_id)

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
        user = User(
            email=data.get('email'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            picture=data.get('picture')
        )
        if 'id' in data:
            user.id = data['id']
        return user
