import re
import logging
from flask import current_app

logger = logging.getLogger(__name__)


class ChunkingService:
    """Splits extracted text into overlapping chunks with metadata."""
    
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def _get_config(self):
        """Get chunk settings from app config or defaults."""
        size = self.chunk_size or current_app.config.get('CHUNK_SIZE', 1000)
        overlap = self.chunk_overlap or current_app.config.get('CHUNK_OVERLAP', 150)
        return size, overlap
    
    def chunk_pages(self, pages: list[dict], document_metadata: dict) -> list[dict]:
        """
        Process pages (output from PDFService) and return a flat list of chunks with metadata.
        
        Args:
            pages: List of {'page_number': int, 'text': str, ...}
            document_metadata: Dict with document_id, user_id, category_id, filename
        
        Returns:
            List of chunk dicts with text and metadata.
        """
        chunk_size, chunk_overlap = self._get_config()
        chunks = []
        chunk_index = 0
        
        for page in pages:
            page_chunks = self._split_text(page['text'], chunk_size, chunk_overlap)
            
            for chunk_text in page_chunks:
                if not chunk_text.strip():
                    continue
                
                chunk = {
                    'text': chunk_text,
                    'metadata': {
                        'document_id': document_metadata['document_id'],
                        'user_id': document_metadata['user_id'],
                        'category_id': document_metadata.get('category_id'),
                        'filename': document_metadata['filename'],
                        'page_number': page['page_number'],
                        'chunk_index': chunk_index,
                    }
                }
                chunks.append(chunk)
                chunk_index += 1
        
        logger.info(f"Created {len(chunks)} chunks for document {document_metadata.get('filename')}")
        return chunks
    
    def _split_text(self, text: str, chunk_size: int, overlap: int) -> list[str]:
        """
        Split text into overlapping chunks, trying to respect sentence boundaries.
        """
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            if end >= len(text):
                chunks.append(text[start:])
                break
            
            # Try to find a sentence boundary (. ! ?) near the end of the chunk
            split_pos = self._find_sentence_boundary(text, end, window=100)
            
            chunk = text[start:split_pos].strip()
            if chunk:
                chunks.append(chunk)
            
            # Next chunk starts with overlap
            start = max(start + 1, split_pos - overlap)
        
        return chunks
    
    def _find_sentence_boundary(self, text: str, pos: int, window: int = 100) -> int:
        """
        Look backward from pos within a window for a sentence-ending punctuation.
        Returns the best split position.
        """
        search_start = max(0, pos - window)
        segment = text[search_start:pos]
        
        # Look for sentence-ending patterns
        matches = list(re.finditer(r'[.!?]\s', segment))
        
        if matches:
            last_match = matches[-1]
            return search_start + last_match.end()
        
        # Fall back to whitespace
        whitespace_matches = list(re.finditer(r'\s', segment))
        if whitespace_matches:
            last_ws = whitespace_matches[-1]
            return search_start + last_ws.end()
        
        return pos  # Hard cut
