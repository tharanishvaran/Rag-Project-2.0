from app.extensions import db


class MessageSource(db.Model):
    """Source citation for an AI response — links answer to document chunks."""
    
    __tablename__ = 'message_sources'
    
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('chat_messages.id', ondelete='CASCADE'), nullable=False, index=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id', ondelete='SET NULL'), nullable=True, index=True)
    page_number = db.Column(db.Integer, nullable=True)
    chunk_id = db.Column(db.String(255), nullable=True)  # ChromaDB chunk ID
    relevance_score = db.Column(db.Float, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'message_id': self.message_id,
            'document_id': self.document_id,
            'filename': self.document.original_filename if self.document else None,
            'page_number': self.page_number,
            'chunk_id': self.chunk_id,
            'relevance_score': round(self.relevance_score, 4) if self.relevance_score else None,
        }
    
    def __repr__(self):
        return f'<MessageSource msg={self.message_id} doc={self.document_id} page={self.page_number}>'
