import os
import uuid
import re
import logging
from werkzeug.utils import secure_filename
from flask import current_app

from app.extensions import db
from app.models.document import Document
from app.document_processor.processor import DocumentProcessor
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.vector_service import VectorService

logger = logging.getLogger(__name__)

# Backend root — used to resolve relative folder paths
_BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class DocumentService:
    """Handles document upload, processing, and deletion."""
    
    def __init__(self):
        self.doc_processor = DocumentProcessor()
        self.chunking_service = ChunkingService()
        self.embedding_service = EmbeddingService()
        self.vector_service = VectorService()
    
    def save_and_process(self, file, user_id: int, category_id: int = None) -> Document:
        """
        Save an uploaded file, extract text (PDF, DOCX, PPTX, TXT, MD, Images), create embeddings, store in ChromaDB.
        
        Returns the Document model instance.
        """
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        # Always resolve to absolute path relative to backend root
        if not os.path.isabs(upload_folder):
            upload_folder = os.path.join(_BACKEND_ROOT, upload_folder)
        upload_folder = os.path.normpath(upload_folder)
        os.makedirs(upload_folder, exist_ok=True)
        
        # Safely preserve user's original filename while handling edge cases
        raw_name = file.filename or "uploaded_document"
        clean_display_name = os.path.basename(raw_name).strip()
        clean_display_name = re.sub(r'[\x00-\x1f\x7f]', '', clean_display_name)
        if not clean_display_name:
            clean_display_name = "uploaded_document.pdf"
            
        ext = os.path.splitext(clean_display_name)[1].lower()
        if not ext:
            sec_name = secure_filename(raw_name)
            ext = os.path.splitext(sec_name)[1].lower() or '.pdf'

        from app.services.storage_service import get_storage_service
        storage_service = get_storage_service()

        stored_filename = f"{uuid.uuid4().hex}{ext}"
        file_path = storage_service.save_file(file, stored_filename)
        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        
        # Create document record in MySQL with UPLOADED status & 0% progress
        document = Document(
            user_id=user_id,
            category_id=category_id,
            original_filename=clean_display_name,
            stored_filename=stored_filename,
            file_path=file_path,
            file_size=file_size,
            upload_status='UPLOADED',
            processing_progress=0,
        )
        db.session.add(document)
        db.session.commit()
        
        # Dispatch Celery background processing task with fallback
        try:
            from app.tasks.document_tasks import process_document_task
            process_document_task.delay(document.id)
            logger.info(f"Dispatched Celery process_document_task for Document ID {document.id}")
        except Exception as cel_err:
            logger.warning(f"Celery dispatch notice for Doc {document.id}: {cel_err}. Triggering daemon fallback...")
            import threading
            try:
                app_obj = current_app._get_current_object()
                threading.Thread(
                    target=self._fallback_background_process,
                    args=(app_obj, document.id),
                    daemon=True
                ).start()
            except Exception as err:
                logger.error(f"Fallback daemon thread error for doc {document.id}: {err}")

        return document

    def _fallback_background_process(self, app, document_id: int):
        """Fallback executor if Celery broker is offline during local dev."""
        with app.app_context():
            try:
                from app.tasks.document_tasks import process_document_task
                process_document_task(document_id)
            except Exception as e:
                logger.error(f"Fallback background processing error: {e}")
    
    def _process_document(self, document: Document, file_path: str):
        """Internal: extract, chunk, embed, and store a document."""
        
        # 1. Extract text sections by format
        pages = self.doc_processor.extract_text(file_path)
        document.total_pages = max((p.get('page_number', 1) for p in pages), default=1)
        db.session.flush()

        
        # 2. Chunk the text with metadata
        doc_metadata = {
            'document_id': document.id,
            'user_id': document.user_id,
            'category_id': document.category_id,
            'filename': document.original_filename,
        }
        chunks = self.chunking_service.chunk_pages(pages, doc_metadata)
        
        if not chunks:
            raise ValueError('No text chunks could be created from this document.')
        
        # 3. Generate embeddings in batch
        texts = [c['text'] for c in chunks]
        embeddings = self.embedding_service.embed_documents(texts)
        
        # 4. Store in ChromaDB
        self.vector_service.add_chunks(chunks, embeddings)
    
    def delete_document(self, document_id: int, user_id: int) -> bool:
        """
        Delete a document: removes file, MySQL record, and ChromaDB embeddings.
        Returns True if deleted, False if not found.
        """
        document = Document.query.filter_by(id=document_id, user_id=user_id).first()
        
        if not document:
            return False
        
        # 1. Delete ChromaDB embeddings
        try:
            self.vector_service.delete_by_document(document_id, user_id)
        except Exception as e:
            logger.error(f'Failed to delete ChromaDB embeddings for doc {document_id}: {e}')
        
        # 2. Delete physical file via StorageService
        try:
            from app.services.storage_service import get_storage_service
            get_storage_service().delete_file(document.stored_filename)
        except Exception as e:
            logger.error(f'Failed to delete file for doc {document_id}: {e}')
        
        # 3. Delete MySQL record
        db.session.delete(document)
        db.session.commit()
        
        return True
    
    def get_user_documents(self, user_id: int, category_id: int = None) -> list:
        """Get all documents for a user, optionally filtered by category."""
        query = Document.query.filter_by(user_id=user_id)
        
        if category_id is not None:
            query = query.filter_by(category_id=category_id)
        
        documents = query.order_by(Document.created_at.desc()).all()
        return [d.to_dict() for d in documents]
    
    def get_document(self, document_id: int, user_id: int) -> Document:
        """Get a single document, ensuring it belongs to the user."""
        return Document.query.filter_by(id=document_id, user_id=user_id).first()
    
    def update_category(self, document_id: int, user_id: int, category_id: int) -> Document:
        """Update the category of a document."""
        document = Document.query.filter_by(id=document_id, user_id=user_id).first()
        
        if not document:
            raise ValueError('Document not found.')
        
        document.category_id = category_id
        db.session.commit()
        
        return document
