# 🧠 Sharp AI — Argumentation Combat Training & Debate Coach

<div align="center">

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi&logoColor=white)](#prerequisites)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com/)
[![Groq](https://img.shields.io/badge/Groq-llama--3.3-orange?style=for-the-badge)](#open-ai-api-completion)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-0284C7?style=for-the-badge)](#retrieval-augmented-generation)
<br/>
[![Live Demo](https://img.shields.io/badge/Demo-sharp--ai--ipp6.onrender.com-FF5733?style=for-the-badge&logo=google-chrome&logoColor=white)](https://sharp-ai-ipp6.onrender.com/docs)

---

**Sharp AI** is a professional-grade FastAPI microservice designed for static topic generation and dynamic debate combat training. Powered by **LangChain**, **ChromaDB**, **GPT-4o-mini**, and **Groq** models, the service offers difficulty-scaled debate scenarios, real-time hints, answer evaluations, and interactive quizzes. When OpenAI API keys are absent, it automatically employs smart `FakeEmbeddings` for vector store initializations, facilitating keyless local development.

</div>


---

## 🛠️ Technical Architecture

Sharp AI leverages a Retrieval-Augmented Generation (RAG) loop to serve custom topic structures and maintain dynamic debate contexts.

```
+-------------------------------------------------------------+
|                     TRADITIONAL BACKEND                     |
|  (Node.js/Postgres Reverse Proxy or Mobile App API Calls)   |
+------------------------------+------------------------------+
                               | (HTTP POST /v1/training/...)
                               v
+-------------------------------------------------------------+
|                      SHARP AI BACKEND                       |
|   Exposes routes, manages slowapi rate limits, handles CORS  |
+------------------------------+------------------------------+
                               |
                               +------------------------------+
                               |                              |
                               v                              v
+------------------------------+------+       +---------------+---------------+
|       SERVICE ORCHESTRATION         |       |        VECTOR DATABASE        |
| - `ai_service.py` (GPT loop)        | <---> | - ChromaDB (local persistence)|
| - `material_service.py` (VDB loader)|       | - Embedded context docs       |
+------------------------------+------+       +-------------------------------+
                               |
                               v
+------------------------------+------+
|                     OPENAI GPT API                          |
|  Generates topic cards, quizzes, hints, and evaluations     |
+-------------------------------------------------------------+
```

### Core Code Modules & Responsibilities

*   `app/api/` Layer:
    *   [`routes/training.py`](app/api/routes/training.py): Difficulty-aware training generators, evaluation loops, and random/category-specific quiz endpoints.
    *   [`routes/materials.py`](app/api/routes/materials.py): Endpoints for uploading and embedding static debate materials.
    *   [`routes/topics.py`](app/api/routes/topics.py): Category and topic administration routes.
*   `app/services/` Layer:
    *   [`ai_service.py`](app/services/ai_service.py): Prompt construction, LangChain execution, and GPT-4o-mini structured JSON outputs parser.
    *   [`material_service.py`](app/services/material_service.py): Integrates with ChromaDB, loading local document embeddings for RAG-assisted queries.
    *   [`progress_service.py`](app/services/progress_service.py): Manages user scores, training milestones, and performance tracking.

---

## ⚡ Core Integration Interfaces

<details>
<summary><b>📚 Retrieval-Augmented Generation (RAG) with ChromaDB</b></summary>

The service stores debate materials as vector embeddings inside a local ChromaDB instance. When a user starts a debate training session on a specific topic, the service performs a similarity search to fetch relevant arguments, statistics, and counter-arguments to feed directly into the LLM system prompt.
</details>

<details>
<summary><b>🎓 Difficulty-Scaled Quiz Generator</b></summary>

Generates multiple-choice questions dynamically tailored to the user's skill level (`Beginner`, `Intermediate`, `Advanced`). The questions evaluate argumentative logic, fallacies, and dodge maneuvers, saving progress logs to a local SQL database.
</details>

<details>
<summary><b>⏱️ Rate Limiting & Security Gateway</b></summary>

Integrates `slowapi` to protect against token exhaustion. Configures strict, fine-grained rate limits (e.g., 30 requests per minute for LLM endpoints) and handles CORS bindings for local and docker deployments.
</details>

---

## 🚀 Getting Started

### 1. Requirements
*   Python 3.10+
*   Virtual environment manager (`venv`)
*   Local database engine or Docker setup

### 2. Configurations Setup
1.  Copy `.env.example` to a new file named `.env`:
    ```bash
    cp .env.example .env
    ```
2.  Add your OpenAI API key and adjust the environment configurations:
    ```env
    OPENAI_API_KEY=sk-proj-your-api-key-here
    OPENAI_MODEL=gpt-4o-mini
    CHROMA_PATH=./app/data/chroma_db
    DEBUG=False

    # Optional: Set GROQ API Key to switch completion client from OpenAI to Groq
    GROQ_API_KEY=your_groq_key_here
    GROQ_MODEL=llama-3.3-70b-versatile
    ```

### 3. Installation & Run
Build the environment and install dependencies:
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

Run the development server using Uvicorn:
```bash
uvicorn app.main:app --reload
```
The server will start at `http://127.0.0.1:8000`. You can inspect the Swagger interactive docs at `http://127.0.0.1:8000/docs`.

### 4. Running Test Scenarios
To run the automated integration test suite:
```bash
# Test Core Data (Categories, Topics)
python tests/test_flow_01_core.py

# Test AI Material Generation
python tests/test_flow_02_materials.py

# Test AI Quizzes
python tests/test_flow_03_quizzes.py

# Test AI Debate Coach
python tests/test_flow_04_debate.py
```

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).
