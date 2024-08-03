import uuid
from enum import Enum

from sqlalchemy import Column, String, DateTime, ForeignKey, func, Integer
from sqlalchemy.orm import relationship

from .. import db



class QuizType(Enum):
    LANGUAGE = "language"
    QUESTIONS = "questions"

from enum import Enum
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, func, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from .. import db

class QuizType(Enum):
    LANGUAGE = "language"
    QUESTIONS = "questions"

class Quiz(db.Model):
    __tablename__ = 'quiz'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_owner_id = Column(String(36), ForeignKey('user.id'))
    title = Column(String(255))
    created_date = Column(DateTime, default=func.now())
    lng = Column(String(50))  # New column for quiz language
    type = Column(String(20), nullable=False, default='QUESTIONS')

    owner = relationship("User", back_populates="quizzes")
    questions = relationship("Question", back_populates="quiz")
    page_scans = relationship("PageScan", back_populates="quiz")
    prep_sessions = relationship("PrepSession", back_populates="quiz")

    def __init__(self, title, user_owner_id, lng=None, type=QuizType.QUESTIONS):
        self.title = title
        self.user_owner_id = user_owner_id
        self.lng = lng
        self.type = type

class Question(db.Model):
    __tablename__ = 'question'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    quiz_id = Column(String(36), ForeignKey('quiz.id'))
    page_scan_id = Column(String(36), ForeignKey('page_scan.id'))
    question_text = Column(String(1000))
    answer = Column(String(1000))
    difficulty_level = Column(db.Integer)
    position = Column(Integer)  # New column

    quiz = relationship("Quiz", back_populates="questions")
    page_scan = relationship("PageScan", back_populates="questions")
    answers = relationship("Answer", back_populates="question")  # Add this line


class Answer(db.Model):
    __tablename__ = 'answer'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'))
    question_id = db.Column(db.String(36), db.ForeignKey('question.id'))
    prep_session_id = db.Column(db.String(36), db.ForeignKey('prep_session.id'))  # New field
    answer_text = db.Column(db.String(1000))
    audio_file_name = db.Column(db.String(255))
    date = db.Column(db.DateTime, default=db.func.now())
    feedback = db.Column(db.String(1000))
    correctness = db.Column(db.Float)
    completeness = db.Column(db.Float)

    user = db.relationship("User", back_populates="answers")
    question = db.relationship("Question", back_populates="answers")
    prep_session = db.relationship("PrepSession", back_populates="answers")  # New relationship

class PrepSession(db.Model):
    __tablename__ = 'prep_session'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'))
    quiz_id = db.Column(db.String(36), db.ForeignKey('quiz.id'))
    start_time = db.Column(db.DateTime, default=db.func.now())
    end_time = db.Column(db.DateTime)
    status = db.Column(db.String(20))  # 'in_progress', 'completed', 'abandoned'
    score = db.Column(db.Float)
    lng = db.Column(db.String(50))  # New column added

    user = db.relationship("User", back_populates="prep_sessions")
    quiz = db.relationship("Quiz", back_populates="prep_sessions")
    answers = db.relationship("Answer", back_populates="prep_session")

    def get_ordered_answers(self):
        return Answer.query.filter(Answer.prep_session_id == self.id) \
            .order_by(Answer.date) \
            .all()
    def get_current_question(self):
        answered_question_ids = [answer.question_id for answer in self.answers]
        next_question = Question.query.filter(
            Question.quiz_id == self.quiz_id,
            ~Question.id.in_(answered_question_ids) # NOT in
        ).order_by(Question.position, Question.id).first()
        return next_question

    def get_distinct_answered_questions_count(self):
        return db.session.query(func.count(func.distinct(Answer.question_id))) \
            .filter(Answer.prep_session_id == self.id) \
            .scalar()

    def get_total_quiz_questions_count(self):
        return Question.query.filter_by(quiz_id=self.quiz_id).count()

class PageScan(db.Model):
    __tablename__ = 'page_scan'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    quiz_id = Column(String(36), ForeignKey('quiz.id'))
    page_position = Column(db.Integer)
    file_name = Column(String(255))
    created_date = Column(DateTime, default=func.now())

    quiz = relationship("Quiz", back_populates="page_scans")
    questions = relationship("Question", back_populates="page_scan")
