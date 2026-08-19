import json
import logging
from flask import current_app
from app.services.embedding_service import EmbeddingService
from app.services.vector_service import VectorService
from app.services.gemini_service import GeminiService
from app.services.ollama_service import OllamaService

logger = logging.getLogger(__name__)


class ExamPrepService:
    """Handles Exam Preparation Strategy, AI Study Planner, Topic Priorities, Paper Analysis, and Expected Questions."""
    
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_service = VectorService()
        self.gemini_service = GeminiService()
        self.ollama_service = OllamaService()

    def _get_context(self, user_id: int, query: str = "syllabus questions exam units", category_id: int = None) -> str:
        try:
            emb = self.embedding_service.embed_query(query)
            results = self.vector_service.query(emb, user_id, n_results=6, category_id=category_id)
            if not results:
                return "No document context uploaded."
            chunks = [f"[Document: {r['metadata'].get('filename', 'Doc')}]\n{r['text']}" for r in results]
            return "\n\n---\n\n".join(chunks)
        except Exception as e:
            logger.warning(f"Error fetching context for exam prep: {e}")
            return "General Knowledge Mode"

    def _call_llm(self, prompt: str) -> str:
        use_gemini = bool(current_app.config.get('GEMINI_API_KEY'))
        if use_gemini:
            try:
                return self.gemini_service.generate_answer(context="", question=prompt)
            except Exception as e:
                logger.warning(f"Gemini call failed in ExamPrepService: {e}")
        return self.ollama_service.generate_answer(context="", question=prompt)

    def generate_strategy(self, user_id: int, subject: str, unit: str, exam_type: str, days_remaining: int, category_id: int = None) -> str:
        context = self._get_context(user_id, f"{subject} {unit} syllabus exam preparation", category_id)
        prompt = f"""You are an expert academic mentor and exam strategist.
Subject: {subject}
Unit: {unit if unit else 'All Units'}
Exam Type: {exam_type}
Days Remaining until Exam: {days_remaining} days

UPLOADED SYLLABUS & NOTES CONTEXT:
{context}

Generate a comprehensive, highly effective Exam Preparation Strategy.
Structure your output into:
1. 🎯 Overall Strategy & Mindset
2. 📖 Core Focus Topics for {unit if unit else 'All Units'}
3. ⏱️ Time Management & Daily Breakdown (for {days_remaining} days)
4. 📝 High-Yield Revision Techniques & Formulae/Key Concepts
5. ⚠️ Common Pitfalls & How to Avoid Them"""
        return self._call_llm(prompt)

    def generate_study_plan(self, user_id: int, subject: str, days_remaining: int, category_id: int = None) -> dict:
        context = self._get_context(user_id, f"{subject} units syllabus modules topics", category_id)
        prompt = f"""You are an AI Study Planner. Create an adaptable day-by-day study schedule for a student taking an exam in {days_remaining} days for the subject "{subject}".

DOCUMENT CONTEXT:
{context}

Respond ONLY in valid JSON format matching this structure:
{{
  "subject": "{subject}",
  "total_days": {days_remaining},
  "plan": [
    {{ "day": 1, "focus": "Unit 1 - Core Concepts", "activities": ["Read notes", "Practice 2-mark Qs"], "status": "pending" }},
    {{ "day": 2, "focus": "Unit 2 - Advanced Topics", "activities": ["Solve previous papers", "Diagram practice"], "status": "pending" }}
  ],
  "recommendation": "Focus heavily on weak areas during revision days."
}}"""
        raw = self._call_llm(prompt)
        try:
            # Clean JSON codeblock wrappers if present
            cleaned = raw.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            return json.loads(cleaned.strip())
        except Exception:
            return {
                "subject": subject,
                "total_days": days_remaining,
                "plan": [
                    {"day": d, "focus": f"Day {d}: Unit & Revision Focus", "activities": ["Review syllabus notes", "Attempt practice quiz"], "status": "pending"}
                    for d in range(1, days_remaining + 1)
                ],
                "recommendation": raw
            }

    def detect_important_topics(self, user_id: int, subject: str, category_id: int = None) -> dict:
        context = self._get_context(user_id, f"{subject} question papers syllabus topics weightage", category_id)
        prompt = f"""Analyze the syllabus and previous question papers for subject "{subject}".
Identify topic importance based on frequency and exam weightage.

DOCUMENT CONTEXT:
{context}

Respond ONLY in valid JSON format:
{{
  "high_priority": [
    {{ "topic": "Topic Name", "reason": "Asked in 80% of previous papers (15 marks)", "weightage": "High" }}
  ],
  "medium_priority": [
    {{ "topic": "Topic Name", "reason": "Frequently asked as 5-mark question", "weightage": "Medium" }}
  ],
  "low_priority": [
    {{ "topic": "Topic Name", "reason": "Basic introductory concepts (2 marks)", "weightage": "Low" }}
  ]
}}"""
        raw = self._call_llm(prompt)
        try:
            cleaned = raw.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            return json.loads(cleaned.strip())
        except Exception:
            return {
                "high_priority": [{"topic": "Core Fundamentals", "reason": "Essential for exam", "weightage": "High"}],
                "medium_priority": [{"topic": "Secondary Modules", "reason": "Moderate frequency", "weightage": "Medium"}],
                "low_priority": [{"topic": "Introduction & History", "reason": "Basic definitions", "weightage": "Low"}]
            }

    def analyze_previous_papers(self, user_id: int, subject: str, category_id: int = None) -> str:
        context = self._get_context(user_id, f"{subject} previous question paper questions patterns marks", category_id)
        prompt = f"""Analyze uploaded previous question papers and syllabus for subject "{subject}".

DOCUMENT CONTEXT:
{context}

Provide a detailed Previous Question Paper Breakdown:
1. 🔁 Frequently Repeated Questions
2. 📊 Unit-Wise Question & Mark Distribution
3. 💡 Question Patterns (MCQs, Short answers, Long analytical questions)
4. 🔑 Must-Study High Yield Topics"""
        return self._call_llm(prompt)

    def generate_expected_questions(self, user_id: int, subject: str, category_id: int = None) -> str:
        context = self._get_context(user_id, f"{subject} syllabus question paper important topics", category_id)
        prompt = f"""Based on patterns in uploaded syllabus and previous papers for subject "{subject}", generate AI-Predicted Expected Questions for the upcoming exam.

DOCUMENT CONTEXT:
{context}

Categorize into:
1. 📌 Predicted 2-Mark Short Questions
2. 📌 Predicted 5-Mark Medium Questions
3. 📌 Predicted 10/15-Mark Essay & Analytical Questions
(Note: Present these as AI pattern predictions based on syllabus weightage and past frequency)."""
        return self._call_llm(prompt)
