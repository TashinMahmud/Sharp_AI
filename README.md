# Debate Quiz API

FastAPI backend for AI-powered debate conversations

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

This project includes highly visual scenario test scripts simulating frontend calls. Ensure the local server is running, then execute them in another terminal:

```bash
# Test Core Data (Categories, Topics)
python tests/test_flow_01_core.py

# Test AI Material Generation
python tests/test_flow_02_materials.py

# Test AI Quizzes
python tests/test_flow_03_quizzes.py

# Test AI Debate Coach (Memory & Adversarial Personas)
python tests/test_flow_04_debate.py
```

## 📖 Complete Documentation

The project root now contains comprehensive instructions for connecting a Postgres/Node.js backend to this FastAPI microservice:
1. `API_DOCUMENTATION.md`: Exact JSON Request/Response schemas.
2. `BACKEND_ARCHITECTURE_GUIDE.md`: Deep dive into how ChromaDB replaces Postgres for AI memory features.
3. `POSTGRES_PRISMA_SCHEMA.md`: Proposed `schema.prisma` file perfectly matching the AI outputs.


## 📚 Features

- AI debate conversations with persistent memory
- Automatic conversation summarization
- Semantic search across past sessions
- Quiz generation and argument evaluation

## �️ Tech Stack

Built with **ChromaDB**, **LangChain**, and **RAG** (Retrieval-Augmented Generation) for intelligent conversation memory.

## �📄 License

MIT License
