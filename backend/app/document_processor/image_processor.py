import logging
from PIL import Image

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Performs OCR on image files (.jpg, .jpeg, .png, .webp) using pytesseract."""
    
    @staticmethod
    def extract(file_path: str) -> list[dict]:
        try:
            import pytesseract
        except ImportError:
            raise ValueError(
                "pytesseract module is missing. Please install pytesseract and system Tesseract OCR."
            )
            
        try:
            img = Image.open(file_path)
        except Exception as e:
            raise ValueError(f"Failed to open image file: {str(e)}")

        try:
            extracted_text = pytesseract.image_to_string(img).strip()
        except Exception as e:
            logger.warning(f"Tesseract OCR failed or not configured on host system: {e}")
            raise ValueError(
                "Unable to extract text from this image using system OCR. Please ensure the image contains clear, readable text or try uploading a PDF/Word version."
            )
            
        if not extracted_text:
            raise ValueError(
                "Unable to extract readable text from this image. Please upload a clearer image of handwritten notes or document pages."
            )
            
        logger.info(f"Extracted {len(extracted_text)} chars from image {file_path} via OCR")
        return [{
            'page_number': 1,
            'section': 'Image OCR Extracted Text',
            'text': extracted_text,
            'file_type': 'image'
        }]
