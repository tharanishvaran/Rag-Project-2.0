import os
import requests
import logging
from flask import current_app

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are Smart Doc AI, an intelligent academic assistant helping college students.

Instructions:
- Prioritize information from the student's uploaded document context below whenever available, citing sources.
- If the question is NOT covered by the provided document context (or no documents match), answer the question completely and accurately using your general knowledge.
- Provide thorough, clear, detailed, and complete explanations. Never cut off or abbreviate code snippets or answers.
- Always provide complete, fully runnable code blocks when explaining programs or algorithms.
- Structure your response cleanly using headings, bullet points, and code blocks for maximum clarity."""


class GeminiService:
    """Communicates with Google Gemini API using high-performance HTTP REST calls."""

    def generate_answer(
        self, 
        context: str, 
        question: str, 
        explanation_mode: str = 'normal', 
        language: str = 'English', 
        history: list = None
    ) -> str:
        """
        Generate an answer using Google Gemini REST API given context, question, mode, and language.
        """
        api_key = current_app.config.get('GEMINI_API_KEY')
        if not api_key:
            raise ValueError('GEMINI_API_KEY is not configured.')

        preferred_model = current_app.config.get('GEMINI_MODEL', 'gemini-1.5-flash')
        max_tokens = current_app.config.get('GEMINI_MAX_TOKENS', 4096)
        candidate_models = [preferred_model, 'gemini-1.5-flash', 'gemini-2.0-flash', 'gemini-1.5-pro', 'gemini-2.5-flash']
        
        # Deduplicate while preserving order
        models_to_try = []
        for m in candidate_models:
            if m not in models_to_try:
                models_to_try.append(m)

        mode_instructions = {
            'simple': "EXPLAIN LIKE I'M A BEGINNER: Use extremely simple language, simple real-world comparisons, and avoid jargon.",
            'example': "GIVE DETAILED EXAMPLES: Illustrate every concept with step-by-step practical examples.",
            'analogy': "USE ANALOGIES: Use creative analogies from everyday life to explain the concept intuitively.",
            'normal': "Provide a clear, academic explanation."
        }
        style_instruction = mode_instructions.get(explanation_mode, mode_instructions['normal'])

        lang_instruction = ""
        if language and language.lower() != 'english':
            lang_instruction = f"IMPORTANT: Respond in {language}. If technical terms are involved, keep the English term in parentheses alongside the translation."

        history_str = ""
        if history:
            formatted_history = []
            for msg in history[-6:]:  # include up to last 6 turns
                role = "Student" if msg.get('role') == 'user' else "AI Assistant"
                formatted_history.append(f"{role}: {msg.get('content', '')}")
            history_str = "\n" + "\n".join(formatted_history) + "\n"

        prompt = f"""{SYSTEM_PROMPT}

STYLE REQUIREMENT: {style_instruction}
{lang_instruction}

---

PREVIOUS CONVERSATION HISTORY:{history_str if history_str else " None"}

---

CONTEXT FROM DOCUMENTS:
{context}

---

STUDENT'S QUESTION:
{question}

ANSWER:"""

        payload = {
            'contents': [{'parts': [{'text': prompt}]}],
            'generationConfig': {
                'temperature': 0.3,
                'maxOutputTokens': max_tokens,
            }
        }

        last_error = None
        for model_name in models_to_try:
            url = f'https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}'
            try:
                logger.info(f'Trying Gemini model ({model_name})...')
                response = requests.post(url, json=payload, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    candidates = data.get('candidates', [])
                    if candidates and 'content' in candidates[0]:
                        parts = candidates[0]['content'].get('parts', [])
                        if parts and 'text' in parts[0]:
                            answer = parts[0]['text'].strip()
                            if answer:
                                logger.info(f'Gemini model ({model_name}) responded successfully!')
                                return answer
                else:
                    logger.warning(f'Gemini model ({model_name}) status {response.status_code}')
                    last_error = f'HTTP {response.status_code}: {response.text[:150]}'
            except Exception as e:
                logger.warning(f'Gemini model ({model_name}) error: {e}')
                last_error = str(e)

        raise RuntimeError(f'All Gemini models failed. Last error: {last_error}')

