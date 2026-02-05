# AI Debate Backend with Persistent Memory

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.6-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Production-ready FastAPI backend for AI-powered debate conversations with **full persistent memory** across server restarts.

## 🚀 Features

### Core Functionality
- **AI Debate Chat** - Engage in structured debates with AI opponents
- **Quiz Generation** - Generate debate-related quiz questions
- **Hint System** - Get contextual hints during debates
- **Argument Evaluation** - AI evaluates your debate performance

### Advanced Memory Management
- ✅ **Immediate Persistence** - Every conversation turn saved to ChromaDB instantly
- ✅ **Session Reconstruction** - Conversations survive server restarts
- ✅ **Automatic Summarization** - Long conversations auto-summarized (configurable threshold)
- ✅ **Memory Pruning** - Intelligent pruning keeps memory efficient
- ✅ **RAG Retrieval** - Semantic search across all past conversations
- ✅ **User Isolation** - Each user+session combination has separate memory

### Production Features
- **Retry Logic** - Automatic retry with exponential backoff for API failures
- **Rate Limiting** - Built-in rate limiting (30 requests/minute)
- **Error Handling** - Comprehensive error handling and logging
- **Docker Support** - Ready for containerized deployment
- **CORS Enabled** - Pre-configured for frontend integration

---

## 📋 Prerequisites

- **Python 3.12** (tested and verified)
- **OpenAI API Key**
- **Git** (for cloning)

---

## ⚡ Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/TashinMahmud/FastAPI-Ai-Quiz.git
cd FastAPI-Ai-Quiz

# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your OpenAI API key
OPENAI_API_KEY=your-key-here
```

### 3. Run the Server

```bash
uvicorn app.main:app --reload
```

**Server:** http://127.0.0.1:8000  
**API Docs:** http://127.0.0.1:8000/docs

---

## 🧪 Testing

Comprehensive test suite included in `tests/` directory:

```bash
cd tests

# Test basic persistence
python test_api.py

# Test summarization (sends 12 messages)
python test_summarization.py

# Test RAG semantic retrieval
python test_rag.py

# Verify summary persistence
python test_verify_summary.py

# Verify RAG persistence
python test_verify_rag.py

# Manual restart test
python manual_test_before_restart.py
# (restart server)
python manual_test_after_restart.py
```

See [`tests/README.md`](tests/README.md) for detailed testing documentation.

---

## 📁 Project Structure

```
ai_backend/
├── app/
│   ├── api/
│   │   └── routes/
│   │       └── debate.py          # API endpoints
│   ├── core/
│   │   └── config.py              # Configuration
│   ├── schemas/
│   │   └── debate_chat.py         # Pydantic models
│   ├── services/
│   │   ├── ai_service.py          # OpenAI integration
│   │   ├── memory_service.py      # Persistent memory
│   │   └── rag_service.py         # RAG retrieval
│   ├── utils/
│   │   └── prompts.py             # AI prompts
│   ├── data/
│   │   └── chroma_db/             # Persistent storage (auto-created)
│   └── main.py                    # FastAPI app
├── tests/                         # Comprehensive test suite
├── .env.example                   # Environment template
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Docker configuration
└── docker-compose.yml             # Docker Compose setup
```

---

## 🔧 Configuration

Edit `.env` to customize:

```bash
# Memory Management
MEMORY_SUMMARY_TRIGGER=10    # Summarize after N messages
MEMORY_KEEP_LAST=5            # Keep N recent messages after pruning

# OpenAI
OPENAI_MODEL=gpt-4o-mini      # AI model to use
OPENAI_TIMEOUT=30             # API timeout (seconds)
MAX_RETRIES=3                 # Retry attempts
```

---

## 🐳 Docker Deployment

```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d

# Stop
docker-compose down
```

---

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/debate/generate` | POST | Generate debate arguments |
| `/debate/chat` | POST | Debate conversation with memory |
| `/debate/quiz` | POST | Generate quiz questions |
| `/debate/hint` | POST | Get contextual hints |
| `/debate/evaluate` | POST | Evaluate arguments |

Full API documentation: http://127.0.0.1:8000/docs

---

## 🧠 Memory System Architecture

### How It Works

1. **Short-term Memory (RAM)**: Active conversation context using LangChain
2. **Long-term Persistence (ChromaDB)**: Every turn saved immediately to disk
3. **Summarization**: After N messages, conversation is summarized
4. **Memory Pruning**: Old messages removed, summary retained
5. **RAG Retrieval**: Semantic search retrieves relevant past context

### Data Flow

```
User Message → AI Response → Save to RAM → Save to ChromaDB
                                ↓
                         Check if N messages
                                ↓
                    Summarize → Store Summary → Prune RAM
```

### Persistence Guarantee

- ✅ **Immediate**: Every turn saved to disk instantly
- ✅ **Durable**: Survives server crashes and restarts
- ✅ **Scalable**: ChromaDB handles millions of messages
- ✅ **Searchable**: Semantic search across all conversations

---

## 🔐 Security Notes

- **Never commit `.env`** - Contains your API key
- **Use environment variables** - For all sensitive data
- **Rate limiting enabled** - Prevents abuse
- **CORS configured** - Adjust for your frontend domain

---

## 📝 Dependencies

Key packages (see `requirements.txt` for full list):

- **FastAPI** - Web framework
- **LangChain** - Memory management (v0.1.20)
- **ChromaDB** - Vector database for persistence
- **OpenAI** - AI model integration
- **Tenacity** - Retry logic
- **SlowAPI** - Rate limiting

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Powered by [OpenAI](https://openai.com/)
- Memory by [LangChain](https://langchain.com/) + [ChromaDB](https://www.trychroma.com/)

---

## 📞 Support

For issues and questions:
- **GitHub Issues**: [Create an issue](https://github.com/TashinMahmud/FastAPI-Ai-Quiz/issues)
- **Documentation**: Check `/docs` endpoint for API details

---

**Made with ❤️ for production-grade AI applications**
