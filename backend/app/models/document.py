from app.extensions import db
from datetime import datetime


class Document(db.Model):
    """Uploaded PDF document model."""
    
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='SET NULL'), nullable=True, index=True)
    
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False, unique=True)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.BigInteger, nullable=True)  # bytes
    total_pages = db.Column(db.Integer, nullable=True)
    
    # Processing lifecycle status: UPLOADED -> PROCESSING -> INDEXED / FAILED
    upload_status = db.Column(db.String(50), default='UPLOADED', nullable=False, index=True)
    processing_progress = db.Column(db.Integer, default=0, nullable=False)
    total_chunks = db.Column(db.Integer, default=0, nullable=False)
    error_message = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    indexed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    message_sources = db.relationship('MessageSource', backref='document', lazy='dynamic')
    
    @property
    def processing_error(self):
        return self.error_message

    @processing_error.setter
    def processing_error(self, value):
        self.error_message = value

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'original_filename': self.original_filename,
            'stored_filename': self.stored_filename,
            'file_size': self.file_size,
            'total_pages': self.total_pages or 0,
            'upload_status': self.upload_status.upper() if self.upload_status else 'UPLOADED',
            'processing_progress': self.processing_progress or 0,
            'total_chunks': self.total_chunks or 0,
            'error_message': self.error_message,
            'processing_error': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'indexed_at': self.indexed_at.isoformat() if self.indexed_at else None,
        }
    
    def __repr__(self):
        return f'<Document {self.original_filename}>'
