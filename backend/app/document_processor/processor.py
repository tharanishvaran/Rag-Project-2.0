import os
import logging
from app.document_processor.pdf_processor import PDFProcessor
from app.document_processor.docx_processor import DOCXProcessor
from app.document_processor.pptx_processor import PPTXProcessor
from app.document_processor.text_processor import TextProcessor
from app.document_processor.image_processor import ImageProcessor

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """
    Unified master dispatcher that detects document format from extension,
    executes the appropriate format extractor, and returns normalized sections.
    """
    
    @staticmethod
    def extract_text(file_path: str) -> list[dict]:
        if not os.path.exists(file_path):
            raise ValueError(f"File not found: {file_path}")
            
        ext = os.path.splitext(file_path)[1].lower().strip('.')
        logger.info(f"Processing document format: .{ext} for file: {file_path}")
        
        if ext == 'pdf':
            return PDFProcessor.extract(file_path)
        elif ext in ['docx', 'doc']:
            return DOCXProcessor.extract(file_path)
        elif ext in ['pptx', 'ppt']:
            return PPTXProcessor.extract(file_path)
        elif ext == 'txt':
            return TextProcessor.extract(file_path, is_markdown=False)
        elif ext == 'md':
            return TextProcessor.extract(file_path, is_markdown=True)
        else:
            raise ValueError(f"Unsupported document format: .{ext}. Allowed formats: PDF, Word (.docx), Text (.txt), Markdown (.md), PowerPoint (.pptx)")

