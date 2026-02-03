# API Specification

**Base URL:** `http://localhost:8000` (development)

All endpoints accept `Content-Type: application/json` and return JSON.

---

## Endpoints

### Health Check

`GET /health`

**Response**
```json
{"status": "ok"}
```

---

### Generate Arguments

`POST /generate`

Generates main arguments, counter arguments, and rebuttals for a topic.

**Request body**
```json
{
  "topic": "Universal healthcare",
  "difficulty": "easy"
}
```

| Field      | Type   | Required |
|------------|--------|----------|
| topic      | string | yes (1–500 chars) |
| difficulty | string | yes (`easy`, `medium`, `hard`) |

**Response**
```json
{
  "main_arguments": ["Healthcare is a basic human right", "..."],
  "counter_arguments": ["Too expensive for taxpayers", "..."],
  "rebuttals": ["Preventive care reduces long-term costs", "..."]
}
```

---

### Generate Quiz

`POST /quiz`

Creates a multiple-choice question from an argument.

**Request body**
```json
{
  "topic": "Universal healthcare",
  "difficulty": "medium",
  "arguments": ["Healthcare is a basic human right"]
}
```

| Field      | Type     | Required |
|------------|----------|----------|
| topic      | string   | yes      |
| difficulty | string   | yes      |
| arguments  | string[] | yes (min 1) |

**Response**
```json
{
  "question": "Which best supports the argument that healthcare is a basic human right?",
  "options": ["Option A", "Option B", "Option C", "Option D"],
  "correct_answer": 0,
  "explanation": "Option A directly aligns with..."
}
```

| Field          | Type   |
|----------------|--------|
| question       | string |
| options        | string[] (4 items) |
| correct_answer | int (0–3 index) |
| explanation    | string |

---

### Get Hint

`POST /hint`

Returns a hint for a question without revealing the answer.

**Request body**
```json
{
  "question": "Which best supports the argument that healthcare is a basic human right?",
  "arguments": ["Healthcare is a basic human right"]
}
```

| Field     | Type     | Required |
|-----------|----------|----------|
| question  | string   | yes      |
| arguments | string[] | yes      |

**Response**
```json
{
  "hint": "Consider which option directly reflects the core principle mentioned in the argument."
}
```

---

### Evaluate Answer

`POST /evaluate`

Returns constructive feedback on a student's answer.

**Request body**
```json
{
  "question": "Which best supports the argument?",
  "selected_answer": "Option B",
  "correct_answer": "Option A",
  "difficulty": "medium"
}
```

| Field           | Type   | Required |
|-----------------|--------|----------|
| question        | string | yes      |
| selected_answer | string | yes      |
| correct_answer  | string | yes      |
| difficulty      | string | yes      |

**Response**
```json
{
  "feedback": "Good effort. Consider focusing on the key principle of the argument..."
}
```

---

## Error Responses

| Status | Meaning |
|--------|---------|
| 401 | Invalid OpenAI API key |
| 422 | Validation error (invalid or missing fields) |
| 429 | OpenAI rate limit exceeded |
| 500 | Server error (e.g. invalid AI response) |
| 503 | OpenAI service temporarily unavailable |

## Rate Limiting

Each AI endpoint is limited to 30 requests per minute per IP. Exceeding the limit returns 429. The health endpoint is exempt.
