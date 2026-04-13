# ⚡ Sharp AI Core Engine — API Documentation

This document defines the 3 primary stateless endpoints used by the Sharp AI engine.
Everything is deployed and accessible at the base URL: `http://46.62.216.255/ai`

---

## 📖 User Flow

```
1. POST /topics/generate    → User picks a category + writes their stance → AI returns a title + study materials
2. POST /training/generate  → User studies materials, writes their argument → AI evaluates, scores, and counter-argues
3. POST /training/hint      → User scored low and needs help → AI gives a 1-sentence tactical hint
```

---

## 📚 Topics Endpoints

### `POST /topics/generate`
The user picks a category and submits their stance. The AI generates a title and structured 4-part argument material for the user to study.

**Request Body:**
```json
{
  "category": "string",
  "message": "string"
}
```

| Field      | Type   | Description                                      |
|------------|--------|--------------------------------------------------|
| `category` | string | The debate category (e.g. "Religion", "Economy") |
| `message`  | string | The user's initial stance or topic idea           |

**Response:**
```json
{
  "title": "string",
  "ai_message": "string",
  "structured_data": {
    "usage": {
      "prompt_tokens": 0,
      "completion_tokens": 0,
      "totalTokens": 0,
      "totalPrompts": 1,
      "estimated_cost_usd": 0,
      "model": "string"
    }
  }
}
```

**Example Request:**
```json
{
  "category": "Religion",
  "message": "Islam is a peaceful religion"
}
```

**Example Response:**
```json
{
  "title": "Islamic Pacifism and Western Perception",
  "ai_message": "### 1. Answer\nIslam's core theological framework emphasizes peace — the word 'Islam' itself derives from 'salaam' meaning peace. The vast majority of 1.8 billion Muslims live peacefully worldwide.\n\n### 2. Data / Facts\n- 93% of global Muslims condemn extremist violence according to a 2019 Gallup World Poll.\n- Muslim-majority countries like Indonesia and Turkey maintain democratic institutions and interfaith dialogue programs.\n\n### 3. Studies\n- Pew Research Center's comprehensive survey on Muslim attitudes toward extremism across 39 countries.\n\n### 4. Dodge Counter\nPeople say: \"But what about the terrorist attacks carried out in the name of Islam?\" Judging 1.8 billion people by the actions of a fringe minority is like condemning all of medicine because of a few malpractice cases.",
  "structured_data": {
    "usage": {
      "prompt_tokens": 300,
      "completion_tokens": 170,
      "totalTokens": 470,
      "totalPrompts": 1,
      "estimated_cost_usd": 0.00012,
      "model": "gpt-4o-mini"
    }
  }
}
```

---

## 🗣️ Training Endpoints

### `POST /training/generate`
After studying the materials from `/topics/generate`, the user submits their own argument. The AI evaluates their stance against the study materials, provides a score, an evaluation, and a counter-argument — all scaled to the selected difficulty.

**Request Body:**
```json
{
  "category": "string",
  "title": "string",
  "materials": "string",
  "message": "string",
  "difficulty": "Beginner"
}
```

| Field        | Type   | Description                                                        |
|--------------|--------|--------------------------------------------------------------------|
| `category`   | string | The debate category                                                |
| `title`      | string | The title returned from `/topics/generate`                         |
| `materials`  | string | The `ai_message` returned from `/topics/generate` (study material) |
| `message`    | string | The user's own argument after studying the materials               |
| `difficulty` | string | `"Beginner"`, `"Intermediate"`, or `"Advanced"`                    |

**Response:**
```json
{
  "category": "string",
  "title": "string",
  "difficulty": "string",
  "ai_message": "string",
  "evaluation": "string",
  "score": 0.0,
  "structured_data": {
    "usage": {
      "prompt_tokens": 0,
      "completion_tokens": 0,
      "totalTokens": 0,
      "totalPrompts": 1,
      "estimated_cost_usd": 0,
      "model": "string"
    }
  }
}
```

| Field         | Type   | Description                                                       |
|---------------|--------|-------------------------------------------------------------------|
| `category`    | string | Echoed back from input                                            |
| `title`       | string | Echoed back from input                                            |
| `difficulty`  | string | Echoed back from input                                            |
| `ai_message`  | string | AI's 4-part counter-argument scaled to difficulty                 |
| `evaluation`  | string | Strategic assessment of how strong the user's argument was        |
| `score`       | float  | 0.0 (weak/wrong) to 1.0 (perfect)                                |

**Example Request:**
```json
{
  "category": "Religion",
  "title": "Islamic Pacifism and Western Perception",
  "materials": "### 1. Answer\nIslam's core theological framework emphasizes peace — the word 'Islam' itself derives from 'salaam' meaning peace...",
  "message": "Islam is peaceful because the Quran says so and most Muslims are good people.",
  "difficulty": "Beginner"
}
```

**Example Response:**
```json
{
  "category": "Religion",
  "title": "Islamic Pacifism and Western Perception",
  "difficulty": "Beginner",
  "ai_message": "### 1. Answer\nSimply saying 'the Quran says so' is not a debate-winning argument — your opponent will immediately point to verses taken out of context to claim otherwise.\n\n### 2. Data / Facts\n- Over 60% of Americans who hold negative views of Islam have never personally met a Muslim, per a 2020 ISPU poll.\n- Hate crimes against Muslims spiked 67% in election years, driven by media framing rather than actual theology.\n\n### 3. Studies\n- Institute for Social Policy and Understanding (ISPU) annual American Muslim Poll.\n\n### 4. Dodge Counter\nPeople say: \"But the Quran has violent verses.\" Cherry-picking verses without historical context is like reading a surgery textbook and concluding that doctors are violent.",
  "evaluation": "Your argument relied on a vague appeal to scripture and anecdotal goodness. You need concrete data points and specific scriptural context to survive even a basic cross-examination.",
  "score": 0.3,
  "structured_data": {
    "usage": {
      "prompt_tokens": 450,
      "completion_tokens": 180,
      "totalTokens": 630,
      "totalPrompts": 1,
      "estimated_cost_usd": 0.00018,
      "model": "gpt-4o-mini"
    }
  }
}
```

---

### `POST /training/hint`
The user scored low on training and needs help. The AI acts as a stealth coach, providing a 1-sentence strategic hint based on the full context of the materials and their failing argument.

**Request Body:**
```json
{
  "category": "string",
  "title": "string",
  "materials": "string",
  "message": "string",
  "difficulty": "Beginner"
}
```

| Field        | Type   | Description                                             |
|--------------|--------|---------------------------------------------------------|
| `category`   | string | The debate category                                     |
| `title`      | string | The topic title                                         |
| `materials`  | string | The study materials from `/topics/generate`             |
| `message`    | string | The user's weak/failing argument from training          |
| `difficulty` | string | `"Beginner"`, `"Intermediate"`, or `"Advanced"`         |

**Response:**
```json
{
  "hint": "string",
  "structured_data": {
    "usage": {
      "prompt_tokens": 0,
      "completion_tokens": 0,
      "totalTokens": 0,
      "totalPrompts": 1,
      "estimated_cost_usd": 0,
      "model": "string"
    }
  }
}
```

**Example Request:**
```json
{
  "category": "Religion",
  "title": "Islamic Pacifism and Western Perception",
  "materials": "### 1. Answer\nIslam's core theological framework emphasizes peace — the word 'Islam' itself derives from 'salaam' meaning peace...",
  "message": "Islam is peaceful because the Quran says so and most Muslims are good people.",
  "difficulty": "Beginner"
}
```

**Example Response:**
```json
{
  "hint": "Instead of vaguely citing scripture, use the Gallup statistic from the materials showing 93% of Muslims condemn extremism — concrete numbers win debates, not feelings.",
  "structured_data": {
    "usage": {
      "prompt_tokens": 150,
      "completion_tokens": 30,
      "totalTokens": 180,
      "totalPrompts": 1,
      "estimated_cost_usd": 0.00004,
      "model": "gpt-4o-mini"
    }
  }
}
```
