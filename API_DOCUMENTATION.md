# FastAPI AI Quiz Engine - API Documentation

This document outlines all the expected requests and responses for the AI Microservice. The backend team should use these exact payloads when communicating with the FastAPI server.

> **Note**: This server operates as an AI processing engine. It does not connect to Postgres directly. It returns formatted JSON (often including calculated metadata like `usage` tokens) that your Main Application backend should save to Postgres.

## 1. Health Check
Checks if the AI engine is running.
- **Endpoint**: `GET /health`
- **Response**:
```json
{"status": "ok", "version": "1.0.0"}
```

---

## 2. Categories API (`/categories`)

### Create a Category
- **Endpoint**: `POST /categories/`
- **Request Body**:
```json
{
  "user_id": 999,
  "category_name": "Test Science",
  "description": "Optional description string"
}
```
- **Response** (200 OK):
```json
{
  "category_id": 637200359,
  "category_name": "Test Science",
  "created_at": "2026-03-08T23:55:00.000Z",
  "topic_count": 0
}
```

### Get User Categories
- **Endpoint**: `GET /categories/{user_id}`
- **Response** (200 OK): `List[CategoryResponse]` (Array of the category object above).

### Delete a Category
- **Endpoint**: `DELETE /categories/{category_id}`
- **Response** (200 OK):
```json
{
  "message": "Category and all related data deleted successfully",
  "topics_deleted": 0
}
```

---

## 3. Topics API (`/topics`)

### Create a Topic
- **Endpoint**: `POST /topics/`
- **Request Body**:
```json
{
  "user_id": 999,
  "category_id": 637200359,
  "topic_name": "Nuclear Fusion vs Fission",
  "description": "The future of clean energy."
}
```
- **Response** (200 OK):
```json
{
  "topic_id": 164692972,
  "category_id": 637200359,
  "topic_name": "Nuclear Fusion vs Fission",
  "created_at": "2026-03-08T23:55:00.000Z",
  "material_count": 0
}
```

### Generate AI Materials for a Topic
*Note: This is an expensive operation that calls OpenAI to generate arguments, counter-arguments, and rebuttals. It saves them to ChromaDB.*
- **Endpoint**: `POST /topics/{topic_id}/generate-materials`
- **Request Body**:
```json
{
  "user_id": 999,
  "topic_id": 164692972,
  "topic_name": "Nuclear Fusion vs Fission",
  "description": "Optional details to guide the AI",
  "difficulty": 3
}
```
- **Response** (200 OK):
```json
{
  "material_id": 2071453353,
  "topic_id": 164692972,
  "main_arguments": ["Argument 1..."],
  "counter_arguments": ["Counter 1..."],
  "rebuttals": ["Rebuttal 1..."],
  "difficulty": 3,
  "created_at": "2026-03-08T23:55:00.000Z"
}
```

### Get Topics by Category
- **Endpoint**: `GET /topics/category/{category_id}`
- **Response** (200 OK): `List[TopicResponse]`

### Get Single Topic
- **Endpoint**: `GET /topics/{topic_id}`
- **Response** (200 OK): `TopicResponse`

### Delete a Topic
- **Endpoint**: `DELETE /topics/{topic_id}`
- **Response** (200 OK): `{"message": "Topic deleted successfully"}`

---

## 4. Quizzes & Training API (`/training`)

### Generate a Topic Quiz
- **Endpoint**: `POST /training/topic-quiz`
- **Request Body**:
```json
{
  "userId": 999,
  "topicId": 164692972,
  "difficulty": 3
}
```
- **Response** (200 OK):
```json
{
  "question": "Which of the following statements about nuclear fusion is true?",
  "options": [
    "Option 1",
    "Option 2",
    "Option 3",
    "Option 4"
  ],
  "correct_answer": 2,
  "explanation": "Because option 3 is chemically accurate.",
  "usage": {
    "prompt_tokens": 223,
    "completion_tokens": 143,
    "totalTokens": 366,
    "totalPrompts": 1,
    "estimated_cost_usd": 0.00011925,
    "model": "gpt-4o-mini"
  },
  "topic_id": 164692972,
  "topic_name": "Nuclear Fusion vs Fission"
}
```

*(Note: There are also `/training/random-quiz` and `/training/category-quiz` endpoints that take similar JSON payloads, e.g., `categoryId` instead of `topicId`)*

### Evaluate an Answer
- **Endpoint**: `POST /training/evaluate`
- **Request Body**:
```json
{
  "practiceContentId": 164692972,
  "userId": 999,
  "question": "Which of the following statements about nuclear fusion is true?",
  "selected_answer": "Option 3 string",
  "correct_answer": "Option 3 string",
  "difficulty": 3
}
```
- **Response** (200 OK):
```json
{
  "score": 1.0,
  "feedback": "Great job! You correctly identified the right answer.",
  "answer": {
    "selected_answer": "Option 3 string",
    "correct_answer": "Option 3 string"
  },
  "usage": {
    "prompt_tokens": 137,
    "completion_tokens": 40,
    "totalTokens": 177,
    "totalPrompts": 1,
    "estimated_cost_usd": 0.00004455,
    "model": "gpt-4o-mini"
  }
}
```

---

## 5. Debate Coach API (`/training/debate`)
This handles the interactive Conservative Debate Coach persona. It maintains memory based on the `session_id`.

- **Endpoint**: `POST /training/debate`
- **Request Body**:
```json
{
  "userId": 999,
  "session_id": "unique-session-id-123",
  "topicId": 164692972,
  "difficulty": 4,
  "role": "argument",
  "message": "Nuclear fusion is too expensive and complex; we should just focus on expanding solar arrays across the country."
}
```
*Note: Valid choices for `role` are: `argument` (starting a point), `counter` (attacking a point), or `rebuttal` (defending against an attack).*

- **Response** (200 OK):
```json
{
  "ai_message": "Nuclear fusion isn't just a dream; it's a revolution waiting to happen. Solar panels are great, but they only work half the time...",
  "structured_data": {
    "practiceContent": {
      "topicId": 164692972,
      "difficulty": 4,
      "generatedBy": "gpt-4o-mini"
    },
    "practiceAttempt": {
      "userId": 999,
      "score": 0.8
    },
    "usage": {
      "prompt_tokens": 1514,
      "completion_tokens": 143,
      "totalTokens": 1657,
      "totalPrompts": 1,
      "estimated_cost_usd": 0.0003129,
      "model": "gpt-4o-mini"
    }
  }
}
```

---

## 6. Usage & Progress Tracking (`/training/stats`)
Fetches aggregated details of a single user's activity (like win rates, tests taken, etc.)

- **Endpoint**: `GET /training/stats/{user_id}`
- **Response** (200 OK):
```json
{
  "total_quizzes": 2,
  "correct_answers": 2,
  "win_rate": 100.0,
  "topics_practiced": 2
}
```
