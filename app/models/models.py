from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class Quiz(Base):
    __tablename__ = 'quiz'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_owner_id = Column(String(36), ForeignKey('user.id'))
    title = Column(String(255))
    created_date = Column(DateTime, default=func.now())

    owner = relationship("User", back_populates="quizzes")
    questions = relationship("Question", back_populates="quiz")
    page_scans = relationship("PageScan", back_populates="quiz")

class Question(Base):
    __tablename__ = 'question'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    quiz_id = Column(String(36), ForeignKey('quiz.id'))
    page_scan_id = Column(String(36), ForeignKey('page_scan.id'))
    question_text = Column(String(1000))
    answer = Column(String(1000))
    difficulty_level = Column(Integer)

    quiz = relationship("Quiz", back_populates="questions")
    page_scan = relationship("PageScan", back_populates="questions")

class Answer(Base):
    __tablename__ = 'answer'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('user.id'))
    answer_text = Column(String(1000))
    audio_file_name = Column(String(255))
    date = Column(DateTime, default=func.now())
    feedback = Column(String(1000))
    correctness = Column(Float)
    completeness = Column(Float)

    user = relationship("User", back_populates="answers")

class PageScan(Base):
    __tablename__ = 'page_scan'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    quiz_id = Column(String(36), ForeignKey('quiz.id'))
    page_position = Column(Integer)
    file_name = Column(String(255))
    created_date = Column(DateTime, default=func.now())

    quiz = relationship("Quiz", back_populates="page_scans")
    questions = relationship("Question", back_populates="page_scan")

# Note: We've removed the engine creation and table creation from here.
# You should handle database initialization separately, typically in your app's initialization code.