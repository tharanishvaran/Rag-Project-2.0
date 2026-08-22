import logging
from app.services.ocr_service import OCRService

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Performs OCR on image files (.jpg, .jpeg, .png, .webp) using Gemini Multimodal OCR."""
    
    @staticmethod
    def extract(file_path: str) -> list[dict]:
        try:
            with open(file_path, 'rb') as f:
                img_bytes = f.read()
        except Exception as e:
            raise ValueError(f"Failed to read image file: {str(e)}")

        ext = file_path.split('.')[-1].lower()
        mime_map = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png', 'webp': 'image/webp'}
        mime = mime_map.get(ext, 'image/png')

        extracted_text = OCRService.extract_text_from_image_bytes(img_bytes, mime)
            
        if not extracted_text:
            raise ValueError(
                "Unable to extract readable text from this image. Please ensure the image contains clear text or try uploading a PDF/Word version."
            )
            
        logger.info(f"Extracted {len(extracted_text)} chars from image {file_path} via Gemini OCR")
        return [{
            'page_number': 1,
            'section': 'Image OCR Extracted Text',
            'text': extracted_text,
            'file_type': 'image'
        }]
