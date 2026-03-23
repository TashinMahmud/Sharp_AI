# AI Microservice Architecture & Endpoints Guide

This document is designed for the **Main Backend Engineering Team** and future AI Assistants (like Gemini/Claude) who will be building the main orchestration server (e.g., Node.js / Next.js) and the primary PostgreSQL database. 

It explains exactly how the standalone FastAPI AI Microservice operates, how memory is handled, and how your endpoints should interact with it.

---

## 1. Architectural Overview

### The "Two Brain" Split
This project operates on a strict split-responsibility architecture:

1. **Your Main Backend (PostgreSQL + Prisma)**
   - **Handles:** User Authentication, User Profiles, Payments, Subscriptions, and **Permanent Storage** of all generated content (saving quizzes, saving topic names, saving user scores).
   - **Does NOT Handle:** AI Generation, Prompt Engineering, Vector Mathematics.

2. **This FastAPI AI Microservice (ChromaDB + OpenAI)**
   - **Handles:** All AI heavy lifting. It talks to OpenAI, generates JSON quizzes, acts as a Debate Coach, and manages its own internal Vector Database (ChromaDB) for "AI Memory".
   - **Does NOT Handle:** Connecting to PostgreSQL, handling user passwords, or validating web JWTs.

### How The Integration Works (The Core Loop)
Whenever a user wants an AI feature, your Main Backend acts as the middleman:
1. User clicks "Generate Quiz" on the Frontend.
2. Frontend sends an HTTP request to your Main Backend.
3. Your Main Backend sends a formatted JSON request to the FastAPI AI Microservice.
4. The AI Microservice does the AI work and returns a perfectly formatted JSON `Response Payload`.
5. Your Main Backend receives that JSON, extracts the details (like the `score` or `usage` tokens), saves those details into your PostgreSQL database using Prisma, and finally passes the result back to the Frontend.

---

## 2. AI Memory (ChromaDB vs Postgres)

A major point of confusion is often: *"Where is the memory stored if FastAPI doesn't connect to Postgres?"*

The FastAPI app runs its own local Vector Database called **ChromaDB**. It saves files directly to a folder inside the Python codebase (`/app/data/chroma_db`). 

**Why?**
Because Storing raw AI text embeddings and chat history directly in PostgreSQL is incredibly slow and expensive. 
Instead:
- The AI Engine saves the entire background context of a Debate inside its local ChromaDB. 
- Your Main Backend ONLY needs to save the `session_id` (a simple string like `"debate_user123_topic88"`) in Postgres.
- When your Main Backend makes a request to the AI Engine, it passes the `session_id`. The AI engine instantly finds the entire conversation history in its local ChromaDB folder, appends it to the prompt behind the scenes, and replies seamlessly.

---

## 3. Detailed Endpoint Breakdown

The following endpoints represent the API contract. **Your main backend must mirror these exact integer/float types when saving to Postgres.**

> *Note: By default, the AI service uses `gpt-4o-mini` and calculates the `estimated_cost_usd` for you to save in your `Usage` Postgres tables.*

### A. Core Data Preparation

Before the AI can do anything, it needs to know what it is thinking about. You must create a Category, then a Topic, and then instruct the AI to "study" that topic.

#### 1. Create a Category
- **What it does:** Registers a top-level subject area.
- **Your Request:** `POST /categories/`
  ```json
  { "user_id": 101, "category_name": "Philosophy" }
  ```
- **The Output:** Returns `category_id` (an **Integer**). You must save this integer in Postgres.

#### 2. Create a Topic
- **What it does:** Registers a specific subject under a category.
- **Your Request:** `POST /topics/`
  ```json
  { "user_id": 101, "category_id": 637200359, "topic_name": "Utilitarianism" }
  ```
- **The Output:** Returns `topic_id` (an **Integer**). Save this in Postgres.

#### 3. Generate Core Training Materials (CRITICAL)
- **What it does:** Instructs the AI to research the Topic, generate arguments/counter-arguments, and save them permanently into the AI's local ChromaDB. **You cannot generate quizzes or debates until this is run.**
- **Your Request:** `POST /topics/{topic_id}/generate-materials`
  - Requires: `user_id` (int), `topic_id` (int), `topic_name` (string), `difficulty` (int 1-5).
- **The Output:** Returns the generated materials. You can optionally save the `main_arguments` array into Postgres if you want to display it on the frontend.

---

### B. The Quiz Engine

#### 1. Generate a Quiz
- **What it does:** The AI reads its local ChromaDB knowledge on the topic and generates a unique, multiple-choice question on the fly.
- **Your Request:** `POST /training/topic-quiz`
  ```json
  { "userId": 101, "topicId": 164692972, "difficulty": 3 }
  ```
- **The Output:**
  ```json
  {
    "question": "Which defines Utilitarianism?",
    "options": ["Option A", "Option B", "Option C"],
    "correct_answer": 1, 
    "explanation": "Because B is correct.",
    "usage": { "prompt_tokens": 120, "estimated_cost_usd": 0.0001 }
  }
  ```
- **Postgres Action:** Your backend should save the `usage` stats to calculate how much this user is costing you.

#### 2. Evaluate an Answer
- **What it does:** Takes the user's selected answer and compares it against the correct answer, calculating a floating-point score based on how close they were.
- **Your Request:** `POST /training/evaluate`
  ```json
  {
    "practiceContentId": 164692972,
    "userId": 101,
    "question": "Which defines Utilitarianism?",
    "selected_answer": "Option A",
    "correct_answer": "Option B",
    "difficulty": 3
  }
  ```
- **The Output:**
  ```json
  {
    "score": 0.0,
    "feedback": "Incorrect, the right answer was B.",
    "usage": { "prompt_tokens": 50, "estimated_cost_usd": 0.00005 }
  }
  ```
- **Postgres Action:** Save the `score` (Float) to the user's `Progress` or `PracticeAttempt` table in Prisma.

---

### C. The Debate Coach Engine

#### 1. Execute a Debate Turn
- **What it does:** Acts as an elite debate coach. It checks its local memory for the `session_id`, reads past messages, evaluates the user's new argument, and fires back a structured counter-argument or rebuttal.
- **Your Request:** `POST /training/debate`
  ```json
  {
    "userId": 101,
    "session_id": "unique-chat-session-id-1234",
    "topicId": 164692972,
    "difficulty": 4,
    "role": "argument",
    "message": "Utilitarianism is flawed because it ignores individual rights."
  }
  ```
  *(Note: Valid `role` strings are exactly: `"argument"`, `"counter_argument"`, or `"rebuttal"`)*

- **The Output:**
  ```json
  {
    "ai_message": "While individual rights are important, maximizing overall happiness often provides a better societal framework...",
    "structured_data": {
       "practiceContent": { "topicId": 164692972, "difficulty": 4, "generatedBy": "gpt-4o-mini" },
       "practiceAttempt": { "userId": 101, "score": 0.75 },
       "usage": { "totalTokens": 1500, "estimated_cost_usd": 0.0003 }
    }
  }
  ```
- **Postgres Action:** 
  1. Forward the `ai_message` string directly to the Frontend UI so the user can read the response.
  2. Take the `structured_data.practiceAttempt.score` (0.75) and save it in Postgres to track that the user is performing at a 75% debate efficiency.
  3. Extract the `usage` costs and bill them internally.
  4. Save the `session_id` to the User's active chats table so they can resume later.
