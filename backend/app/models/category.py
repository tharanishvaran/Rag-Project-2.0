from app.extensions import db
from datetime import datetime


class Category(db.Model):
    """Document category model."""
    
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    documents = db.relationship('Document', backref='category', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'document_count': self.documents.count(),
            'created_at': self.created_at.isoformat(),
        }
    
    def __repr__(self):
        return f'<Category {self.name}>'


# Default categories to seed on first run
DEFAULT_CATEGORIES = [
    {'name': 'Syllabus', 'description': 'Course syllabi and curriculum documents'},
    {'name': 'Study Notes', 'description': 'Lecture notes and study materials'},
    {'name': 'Previous Question Papers', 'description': 'Past exam and question papers'},
    {'name': 'College Rules', 'description': 'College regulations and guidelines'},
    {'name': 'Reference Materials', 'description': 'Textbooks and reference documents'},
]
