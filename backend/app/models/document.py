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
    
    # Processing status: uploaded → processing → completed / failed
    upload_status = db.Column(
        db.Enum('uploaded', 'processing', 'completed', 'failed', name='upload_status_enum'),
        default='uploaded',
        nullable=False
    )
    processing_error = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    message_sources = db.relationship('MessageSource', backref='document', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'original_filename': self.original_filename,
            'stored_filename': self.stored_filename,
            'file_size': self.file_size,
            'total_pages': self.total_pages,
            'upload_status': self.upload_status,
            'processing_error': self.processing_error,
            'created_at': self.created_at.isoformat(),
        }
    
    def __repr__(self):
        return f'<Document {self.original_filename}>'
