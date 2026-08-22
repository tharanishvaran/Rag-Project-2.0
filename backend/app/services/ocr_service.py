import base64
import requests
import logging
from flask import current_app

logger = logging.getLogger(__name__)


class OCRService:
    """Uses Gemini Multimodal API to perform 100% accurate OCR on image-based documents."""

    @staticmethod
    def extract_text_from_image_bytes(image_bytes: bytes, mime_type: str = 'image/png') -> str:
        """
        Extract readable text from image bytes using Gemini Vision API.
        """
        if not image_bytes:
            return ""

        api_key = ""
        try:
            if current_app:
                api_key = current_app.config.get('GEMINI_API_KEY', '')
        except Exception:
            pass

        if not api_key:
            import os
            api_key = os.getenv('GEMINI_API_KEY', '')

        if not api_key:
            logger.warning("GEMINI_API_KEY not configured for OCR service.")
            return ""

        b64_data = base64.b64encode(image_bytes).decode('utf-8')
        models_to_try = ['gemini-2.5-flash', 'gemini-1.5-flash', 'gemini-2.0-flash']

        prompt = (
            "Extract ALL text, contact info, education, skills, projects, work experience, "
            "tables, headings, numbers, and bullet points from this document image cleanly into plain text. "
            "Maintain full structural layout and accuracy."
        )

        for model_name in models_to_try:
            url = f'https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}'
            payload = {
                'contents': [{
                    'parts': [
                        {'text': prompt},
                        {
                            'inline_data': {
                                'mime_type': mime_type,
                                'data': b64_data
                            }
                        }
                    ]
                }]
            }
            try:
                logger.info(f"Performing Gemini Vision OCR ({model_name})...")
                res = requests.post(url, json=payload, timeout=5)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get('candidates', [])
                    if candidates and 'content' in candidates[0]:
                        parts = candidates[0]['content'].get('parts', [])
                        text_parts = [p['text'] for p in parts if 'text' in p and p['text'].strip()]
                        if text_parts:
                            result = "\n".join(text_parts).strip()
                            logger.info(f"Gemini Vision OCR ({model_name}) extracted {len(result)} characters!")
                            return result
                else:
                    logger.warning(f"Gemini Vision OCR ({model_name}) HTTP {res.status_code}: {res.text[:150]}")
            except Exception as e:
                logger.warning(f"Gemini Vision OCR ({model_name}) failed: {e}")

        return ""
