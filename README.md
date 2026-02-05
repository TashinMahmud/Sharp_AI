# Debate Quiz API

FastAPI backend for AI-powered debate conversations with persistent memory and semantic search.

## ⚡ Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/TashinMahmud/FastAPI-Ai-Quiz.git
cd FastAPI-Ai-Quiz
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### 3. Run Server

```bash
uvicorn app.main:app --reload
```

**Server:** http://127.0.0.1:8000  
**API Docs:** http://127.0.0.1:8000/docs

## 🧪 Testing

```bash
cd tests
python test_api.py
```

## 📚 Features

- AI debate conversations with persistent memory
- Automatic conversation summarization
- Semantic search across past sessions
- Quiz generation and argument evaluation

## 📄 License

MIT License
