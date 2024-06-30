import logging
import uuid

from flask_login import UserMixin
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from .. import db


class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False)
    first_name = Column(String(255))
    last_name = Column(String(255))
    picture = Column(String(255))

    quizzes = relationship("Quiz", back_populates="owner")
    answers = relationship("Answer", back_populates="user")
    prep_sessions = relationship("PrepSession", back_populates="user")  # New relationship

    def __init__(self, email, first_name=None, last_name=None, picture=None):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.picture = picture

    @staticmethod
    def get(email):
        return User.query.filter_by(email=email).first()

    @staticmethod
    def create(email, first_name=None, last_name=None, picture=None):
        user = User(email=email, first_name=first_name, last_name=last_name, picture=picture)
        db.session.add(user)
        db.session.commit()
        logging.info(f"Created new user with email: {email}")
        return user

    @staticmethod
    def get_or_create(email, first_name=None, last_name=None, picture=None):
        user = User.get(email)
        if user is None:
            user = User.create(email, first_name, last_name, picture)
        else:
            user.update(first_name, last_name, picture)
        return user

    def update(self, first_name=None, last_name=None, picture=None):
        if first_name is not None:
            self.first_name = first_name
        if last_name is not None:
            self.last_name = last_name
        if picture is not None:
            self.picture = picture
        db.session.commit()
        logging.info(f"Updated user information for email: {self.email}")

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
        return User.get_or_create(
            email=data.get('email'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            picture=data.get('picture')
        )