# API Documentation: Training Platform

## 🎯 Overview

The backend has been pivoted to an **Argumentation Training Platform**. Users can create personal libraries of topics, generate study materials with AI, and practice through structured quizzes.

**Base URL:** `http://localhost:8000`
**Interactive Docs:** `http://localhost:8000/docs`

---

## 📚 1. Knowledge Library (Categories & Topics)

### Manage Categories
Create categories like "Politics", "Religion", "Economics".

**Create Category**
```http
POST /categories
{
  "user_id": "user_123",
  "category_name": "Religion"
}
```

**Get Categories**
```http
GET /categories/{user_id}
```

---

### Manage Topics
Add topics to categories (e.g., "Creation vs Evolution" inside "Religion").

**Create Topic**
```http
POST /topics
{
  "user_id": "user_123",
  "category_id": "category_uuid",
  "topic_name": "Creation vs Evolution",
  "description": "Defending the Christian view"
}
```

**Get Topics by Category**
```http
GET /topics/category/{category_id}
```

---

## 🧠 2. AI Study Materials

Generate arguments, counter-arguments, and rebuttals for your topics.

**Generate & Save Materials**
```http
POST /topics/{topic_id}/generate-materials
{
  "user_id": "user_123",
  "topic_name": "Creation vs Evolution",
  "difficulty": "medium"
}
```

**Get Saved Materials**
```http
GET /topics/{topic_id}/materials
```
_Returns structured arguments to study._

---

## 🎓 3. Training Mode (Quizzes)

Practice what you've learned through AI-generated quizzes.

### Random Quiz
Test yourself on a random topic from your entire library.
```http
POST /training/random-quiz
{
  "user_id": "user_123",
  "difficulty": "medium"
}
```

### Category Quiz
Test yourself on a random topic within a specific category.
```http
POST /training/category-quiz
{
  "user_id": "user_123",
  "category_id": "category_uuid",
  "difficulty": "medium"
}
```

### Topic Quiz
Test yourself on a specific topic.
```http
POST /training/topic-quiz
{
  "user_id": "user_123",
  "topic_id": "topic_uuid",
  "difficulty": "medium"
}
```

---

## ⚔️ 4. Debate Coach (Context-Aware)

Start a debate on a specific topic. The AI will know all the study materials you generated for this topic and will challenge you on them.

**Start Debate**
```http
POST /training/debate
{
  "user_id": "user_123",
  "session_id": "session_001",
  "topic_id": "topic_uuid",
  "difficulty": "medium",
  "role": "user_argument",
  "message": "I believe that..."
}
```

**Helper Endpoints:**
All training interactions use these helpers:
- `POST /training/hint` (Get hint for quiz)
- `POST /training/evaluate` (Evaluate answer)

### Progress Stats
Track your performance over time.

**Get User Stats**
```http
GET /training/stats/{user_id}
```
_Returns: Total quizzes, correct answers, win rate, and unique topics practiced._

---

## 🛠️ Data Structure

### Category
- `category_id`: UUID
- `category_name`: String
- `user_id`: String

### Topic
- `topic_id`: UUID
- `category_id`: UUID
- `topic_name`: String
- `description`: String

### Material
- `material_id`: UUID
- `topic_id`: UUID
- `main_arguments`: List[String]
- `counter_arguments`: List[String]
- `rebuttals`: List[String]

---

## 🚀 Integration Guide for UI Team

1. **User Onboarding:**
   - User signs up (handled by auth service/firebase)
   - App calls `GET /categories/{user_id}` to show their library.

2. **Library Screen:**
   - User clicks "+" to add category -> `POST /categories`
   - User clicks category -> `GET /topics/category/{id}`
   - User creates topic -> `POST /topics` -> Then immediately `POST /topics/{id}/generate-materials` to populate content.

3. **Study Screen:**
   - Show topic details
   - Call `GET /topics/{id}/materials` to display arguments cards (Flashcards implementation recommended).

4. **Training Tab:**
   - "Quick Practice" button -> `POST /training/random-quiz`
   - "Focus Mode" -> `POST /training/category-quiz`
   - "Focus Mode" -> `POST /training/category-quiz`
   - Display Question -> User selects Option -> Call `POST /training/evaluate` to check answer.

5. **Advanced Practice:**
   - "Debate Coach" button -> Opens Chat UI -> `POST /training/debate` using the `topic_id`.
