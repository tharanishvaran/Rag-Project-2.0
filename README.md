# Smart Doc AI 🎓📚 — Production Ready Student RAG Educational Assistant

> An AI-powered educational platform built with React, Flask, MySQL, ChromaDB, Google Gemini / Ollama, supporting multi-format document uploads (PDF, DOCX, TXT, MD, Images via OCR, PPTX), AI Exam Preparation, Automatic Question Generation, Interactive AI Quizzes, Student Analytics Dashboard, Voice Input & TTS, Multi-language support, and persistent authentication.

---

## 🚀 Overview

**Smart Doc AI 2.0** turns college syllabus materials, textbooks, previous question papers, handwritten notes, and slide decks into an interactive AI study companion.

Key Capabilities:
1. **📚 Multi-Format Document Upload**: Upload PDF, Word (`.docx`), Text (`.txt`), Markdown (`.md`), Images (`.jpg`, `.png` via OCR), and PowerPoint (`.pptx`) simultaneously.
2. **🎯 Exam Preparation Mode**: Generate personalized exam strategies and day-by-day AI study schedules based on days remaining and uploaded syllabus.
3. **📝 Automatic Question Generation**: Generate MCQs, 2-mark short questions, 5-mark conceptual, and 10/15-mark essay questions by topic or mark type.
4. **🧠 AI Quiz Mode**: Take interactive, step-by-step timed quizzes where the AI evaluates answers, calculates scores, provides detailed explanations, and highlights conceptual weaknesses.
5. **📊 Student Performance Dashboard**: Track Total Questions Attempted, Correct Count, Accuracy %, Strong Topics (✓), and Weak Topics (⚠).
6. **🔍 Source Citation**: View exact document names, page/section/slide numbers, and relevance matching for every answer.
7. **📖 Response Style Switcher**: Toggle response modes (`Explain Normally` | `Explain Simply` | `Give Example` | `Give Analogy`).
8. **🔄 Follow-up Questions**: Preserves conversation history context for follow-up Q&A.
9. **🎓 Important Topic Detection**: Priority breakdown (🔥 High, 🟡 Medium, 🟢 Low) based on paper analysis and syllabus coverage.
10. **📑 Previous Question Paper Analysis**: Identify repeated questions, topic frequency, and mark distributions.
11. **🔮 Expected Questions**: AI-predicted exam questions for upcoming tests.
12. **🗣️ Voice Q&A**: Speech-to-text voice questions and text-to-speech AI answer reading.
13. **🌐 Multi-Language Support**: Ask and receive explanations in English, Tamil, Tanglish (Tamil + English), Hindi, Telugu, etc.
14. **🔐 Persistent ChatGPT-style Auth**: JWT tokens stored securely to maintain continuous user sessions.

---

## 🏗️ Architecture

```text
                    STUDENT
                       │
                       ▼
              ┌─────────────────┐
              │  React Frontend │
              │ (Netlify / Dev) │
              └────────┬────────┘
                       │ HTTPS / CORS
                       ▼
              ┌─────────────────┐
              │   Flask API     │
              │ (Render / Dev)  │
              └────────┬────────┘
                       │
          ┌────────────┼─────────────┐
          ▼            ▼             ▼
       MySQL       RAG Pipeline   AI API (Gemini / Ollama)
                       │
                ┌──────┴──────┐
                ▼             ▼
           Embeddings     ChromaDB (Vector Store)
```

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 19 + Vite, React Router v7, Axios, Lucide Icons, Web Speech API |
| **Backend API** | Python 3.10+, Flask 3.0, Flask-CORS, Flask-JWT-Extended, Gunicorn, Flask-Limiter |
| **Relational DB** | MySQL 8.x + SQLAlchemy ORM + PyMySQL |
| **Document Processing** | PyMuPDF (PDF), python-docx (DOCX), python-pptx (PPTX), Pillow + pytesseract (OCR) |
| **Embeddings & Vector Store**| Sentence-Transformers (`all-MiniLM-L6-v2`), ChromaDB |
| **LLM Orchestration** | Google Gemini REST API (`gemini-3.5-flash-lite`) with local Ollama fallback |

---

## ⚙️ Environment Variables

### Backend `.env`

```env
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/smart_doc_ai
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.5-flash-lite
FRONTEND_URL=http://localhost:5173
UPLOAD_FOLDER=uploads
CHROMA_PERSIST_DIRECTORY=chroma_db
```

### Frontend `.env`

```env
VITE_API_URL=http://localhost:5000/api
```

---

## 🚀 Local Development Guide

### 1. Clone & MySQL Setup
```sql
CREATE DATABASE smart_doc_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt
python run.py
```
*(Backend runs on `http://localhost:5000`)*

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
*(Frontend runs on `http://localhost:5173`)*

---

## ☁️ Production Deployment Guide

### Deploying Backend to Render
1. Push your repository to GitHub.
2. Create a **Web Service** on Render pointing to the `backend/` folder.
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `gunicorn run:app`
5. Configure Environment Variables in Render Dashboard (`GEMINI_API_KEY`, `DATABASE_URL`, `FRONTEND_URL`).

### Deploying Frontend to Netlify
1. Create a **New Site from Git** on Netlify pointing to `frontend/`.
2. Build Command: `npm run build`
3. Publish Directory: `dist`
4. Environment Variable: `VITE_API_URL=https://your-render-backend-url.onrender.com/api`

---

## 🌐 Summary of API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/auth/register` | Register new student |
| `POST` | `/api/auth/login` | Login & receive JWT |
| `POST` | `/api/documents/upload` | Multi-format upload (PDF, DOCX, TXT, MD, Images, PPTX) |
| `GET` | `/api/documents` | List uploaded materials |
| `DELETE` | `/api/documents/:id` | Delete material and embeddings |
| `POST` | `/api/chat/ask` | Ask question with RAG, style mode, language & context |
| `POST` | `/api/exam-prep/strategy` | Generate exam strategy |
| `POST` | `/api/exam-prep/study-plan` | Generate AI day-by-day study schedule |
| `POST` | `/api/exam-prep/important-topics` | Priority topic detection (High, Med, Low) |
| `POST` | `/api/exam-prep/paper-analysis` | Analyze previous paper patterns |
| `POST` | `/api/exam-prep/expected-questions` | Predict exam questions |
| `POST` | `/api/quiz/generate-questions` | Generate practice question sets by marks |
| `POST` | `/api/quiz/start-quiz` | Start interactive AI quiz session |
| `POST` | `/api/quiz/evaluate-answer` | Evaluate student answer, score & weakness |
| `GET` | `/api/quiz/dashboard-stats` | Student performance stats (accuracy, strong/weak topics) |

---

## 👨‍💻 Author
**Tharanishvaran** — Student RAG Educational Assistant Project
