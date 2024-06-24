import uuid

from sqlalchemy import Column, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from .. import db


class Quiz(db.Model):
    __tablename__ = 'quiz'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_owner_id = Column(String(36), ForeignKey('user.id'))
    title = Column(String(255))
    created_date = Column(DateTime, default=func.now())

    owner = relationship("User", back_populates="quizzes")
    questions = relationship("Question", back_populates="quiz")
    page_scans = relationship("PageScan", back_populates="quiz")


class Question(db.Model):
    __tablename__ = 'question'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    quiz_id = Column(String(36), ForeignKey('quiz.id'))
    page_scan_id = Column(String(36), ForeignKey('page_scan.id'))
    question_text = Column(String(1000))
    answer = Column(String(1000))
    difficulty_level = Column(db.Integer)

    quiz = relationship("Quiz", back_populates="questions")
    page_scan = relationship("PageScan", back_populates="questions")


class Answer(db.Model):
    __tablename__ = 'answer'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('user.id'))
    answer_text = Column(String(1000))
    audio_file_name = Column(String(255))
    date = Column(DateTime, default=func.now())
    feedback = Column(String(1000))
    correctness = Column(db.Float)
    completeness = Column(db.Float)

    user = relationship("User", back_populates="answers")


class PageScan(db.Model):
    __tablename__ = 'page_scan'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    quiz_id = Column(String(36), ForeignKey('quiz.id'))
    page_position = Column(db.Integer)
    file_name = Column(String(255))
    created_date = Column(DateTime, default=func.now())

    quiz = relationship("Quiz", back_populates="page_scans")
    questions = relationship("Question", back_populates="page_scan")
