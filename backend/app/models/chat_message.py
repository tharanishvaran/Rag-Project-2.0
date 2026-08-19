from app.extensions import db
from datetime import datetime


class ChatMessage(db.Model):
    """Individual chat message (user or assistant)."""
    
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_sessions.id', ondelete='CASCADE'), nullable=False, index=True)
    role = db.Column(db.Enum('user', 'assistant', name='message_role_enum'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    sources = db.relationship('MessageSource', backref='message', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self, include_sources=True):
        data = {
            'id': self.id,
            'session_id': self.session_id,
            'role': self.role,
            'message': self.message,
            'created_at': self.created_at.isoformat(),
        }
        if include_sources and self.role == 'assistant':
            data['sources'] = [s.to_dict() for s in self.sources.all()]
        return data
    
    def __repr__(self):
        return f'<ChatMessage {self.id} [{self.role}]>'
