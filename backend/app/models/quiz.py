from datetime import datetime
from app.extensions import db


class QuizAttempt(db.Model):
    """Model tracking a student's quiz attempt session."""
    __tablename__ = 'quiz_attempts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    subject = db.Column(db.String(100), nullable=True)
    topic = db.Column(db.String(100), nullable=True)
    total_questions = db.Column(db.Integer, default=0)
    score = db.Column(db.Integer, default=0)
    accuracy = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    answers = db.relationship('QuizAnswer', backref='attempt', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'subject': self.subject,
            'topic': self.topic,
            'total_questions': self.total_questions,
            'score': self.score,
            'accuracy': self.accuracy,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class QuizAnswer(db.Model):
    """Model tracking an individual question answer in a quiz."""
    __tablename__ = 'quiz_answers'

    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('quiz_attempts.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    user_answer = db.Column(db.Text, nullable=False)
    correct_answer = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    score_earned = db.Column(db.Float, default=0.0)
    topic_tag = db.Column(db.String(100), nullable=True)
    explanation = db.Column(db.Text, nullable=True)
    weakness_identified = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'attempt_id': self.attempt_id,
            'question': self.question,
            'user_answer': self.user_answer,
            'correct_answer': self.correct_answer,
            'is_correct': self.is_correct,
            'score_earned': self.score_earned,
            'topic_tag': self.topic_tag,
            'explanation': self.explanation,
            'weakness_identified': self.weakness_identified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
