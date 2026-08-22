import logging
from datetime import datetime
from flask import current_app

from app.celery_app import celery
from app.extensions import db
from app.models.document import Document
from app.document_processor.processor import DocumentProcessor
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.vector_service import VectorService
from app.services.storage_service import get_storage_service

logger = logging.getLogger(__name__)


def _update_document_progress(document_id: int, status: str, progress: int, total_chunks: int = None, error_msg: str = None):
    """Helper to update Document model state in MySQL."""
    try:
        doc = Document.query.get(document_id)
        if not doc:
            return None
        doc.upload_status = status
        doc.processing_progress = progress
        if total_chunks is not None:
            doc.total_chunks = total_chunks
        if error_msg is not None:
            doc.error_message = str(error_msg)[:500]
        if status == 'INDEXED':
            doc.indexed_at = datetime.utcnow()
        doc.updated_at = datetime.utcnow()
        db.session.commit()
        return doc
    except Exception as err:
        db.session.rollback()
        logger.error(f"Failed to update document progress (id={document_id}): {err}")
        return None


@celery.task(bind=True, max_retries=3, default_retry_delay=5)
def process_document_task(self, document_id: int):
    """
    Celery task to asynchronously extract, chunk, batch embed, and index document vectors into ChromaDB.
    """
    logger.info(f"Starting process_document_task (Task ID: {self.request.id}, Doc ID: {document_id})")

    # Step 1: Set status = PROCESSING, progress = 5
    doc = _update_document_progress(document_id, 'PROCESSING', 5)
    if not doc:
        logger.error(f"Document {document_id} not found in database.")
        return {'success': False, 'error': 'Document not found'}

    storage_service = get_storage_service()
    file_path = storage_service.get_file_path(doc.stored_filename)

    try:
        # Step 2: Text Extraction (10% -> 25%)
        _update_document_progress(document_id, 'PROCESSING', 10)
        doc_processor = DocumentProcessor()
        pages = doc_processor.extract_text(file_path)
        
        doc.total_pages = max((p.get('page_number', 1) for p in pages), default=1)
        db.session.commit()
        _update_document_progress(document_id, 'PROCESSING', 25)

        # Step 3: Chunking (25% -> 40%)
        chunking_service = ChunkingService()
        doc_metadata = {
            'document_id': doc.id,
            'user_id': doc.user_id,
            'category_id': doc.category_id,
            'filename': doc.original_filename,
        }
        chunks = chunking_service.chunk_pages(pages, doc_metadata)
        if not chunks:
            raise ValueError("No text chunks could be created from this document.")

        total_chunks = len(chunks)
        _update_document_progress(document_id, 'PROCESSING', 40, total_chunks=total_chunks)

        # Step 4: Batch Embedding (50% -> 80%)
        embedding_service = EmbeddingService()
        texts = [c['text'] for c in chunks]
        
        batch_size = 32
        try:
            if current_app:
                batch_size = current_app.config.get('EMBEDDING_BATCH_SIZE', 32)
        except Exception:
            pass

        def on_embed_progress(pct):
            _update_document_progress(document_id, 'PROCESSING', pct)

        embeddings = embedding_service.embed_documents_batch(texts, batch_size=batch_size, progress_callback=on_embed_progress)
        _update_document_progress(document_id, 'PROCESSING', 80)

        # Step 5: Deterministic Batch Vector Insertion into ChromaDB (80% -> 98%)
        vector_service = VectorService()
        v_batch_size = 50
        try:
            if current_app:
                v_batch_size = current_app.config.get('VECTOR_BATCH_SIZE', 50)
        except Exception:
            pass

        def on_vector_progress(pct):
            _update_document_progress(document_id, 'PROCESSING', pct)

        vector_service.add_chunks_batch(chunks, embeddings, batch_size=v_batch_size, progress_callback=on_vector_progress)

        # Step 6: Mark as INDEXED, progress = 100%
        _update_document_progress(document_id, 'INDEXED', 100)
        logger.info(f"Document {document_id} indexed successfully in ChromaDB! ({total_chunks} chunks)")
        return {'success': True, 'document_id': document_id, 'total_chunks': total_chunks}

    except Exception as e:
        logger.warning(f"Error in process_document_task (Doc {document_id}, Retry {self.request.retries}/3): {e}")
        # Retry for transient network or rate-limit failures
        if self.request.retries < self.max_retries:
            countdown = 5 * (2 ** self.request.retries)  # Exponential backoff: 5s, 10s, 20s
            try:
                raise self.retry(exc=e, countdown=countdown)
            except Exception:
                pass

        # Final failure state after retries exhausted
        error_msg = f"Document processing failed: {str(e)}"
        _update_document_progress(document_id, 'FAILED', 0, error_msg=error_msg)
        return {'success': False, 'error': str(e)}
