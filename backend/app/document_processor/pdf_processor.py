try:
    import pymupdf as fitz
except ImportError:
    import fitz

import re
import logging

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Extracts text from PDF documents page by page."""
    
    @staticmethod
    def extract(file_path: str) -> list[dict]:
        pages = []
        try:
            doc = fitz.open(file_path)
        except Exception as e:
            raise ValueError(f"Failed to open PDF: {str(e)}")
        
        total_pages = len(doc)
        total_chars = 0
        
        for page_num in range(total_pages):
            page = doc[page_num]
            raw_text = page.get_text()
            cleaned = PDFProcessor._clean_text(raw_text)
            if cleaned.strip():
                pages.append({
                    'page_number': page_num + 1,
                    'section': f'Page {page_num + 1}',
                    'text': cleaned,
                    'file_type': 'pdf'
                })
                total_chars += len(cleaned)
        
        doc.close()
        
        if total_chars == 0:
            raise ValueError("PDF appears to be empty or a scanned document without extractable text.")
            
        logger.info(f"Extracted {total_chars} chars across {len(pages)} pages from {file_path}")
        return pages

    @staticmethod
    def _clean_text(text: str) -> str:
        if not text:
            return ""
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        text = re.sub(r'\n{3,}', '\n\n', text)
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        return re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text).strip()
