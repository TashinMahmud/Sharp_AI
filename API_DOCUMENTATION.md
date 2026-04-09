# AI Microservice Integration Guide

## 1. Generating a Static Topic (Library Content)

**Endpoint:** `POST /topics/generate`  
**Purpose:** Generates a static, 4-part library topic card (Answer, Data/Facts, Studies, Dodge Counter) for the user to study.

### Input (From Node.js backend to FastAPI)
```json
{
  "userId": 123,
  "topicId": 42,
  "message": "Write a breakdown of the taxation arguments."
}
```

### Output (From FastAPI back to Node.js)
```json
{
  "ai_message": "Topic generated successfully...",
  "structured_data": {
    "practiceContent": {
      "topicId": 42,
      "difficulty": null,
      "generatedBy": "gpt-4o-mini",
      "content": {
        "part1": "...markdown...",
        "part2": "...markdown..."
      }
    },
    "usage": {
      "prompt_tokens": 150,
      "completion_tokens": 300,
      "totalTokens": 450,
      "totalPrompts": 1,
      "estimated_cost_usd": 0.002,
      "model": "gpt-4o-mini"
    }
  }
}
```

### Prisma Mapping:
1. **`PracticeContent` Table:** Insert a new row here using the `structured_data.practiceContent` object. **Note:** Ensure the `difficulty` field is saved as `null` since this is static library material.
2. **`AiUsageLog` / `UserUsage` Table:** Grab the `usage` object. Save the token counts and the `estimated_cost_usd` so we have a receipt of the server cost. Set the `endpointUsed` string to `"/topics/generate"`.

---

## 2. Generating a Training Scenario (Dynamic Debate)

**Endpoint:** `POST /training/generate`  
**Purpose:** Generates a dynamic debate scenario scaled perfectly to a specific difficulty level.

### Input (From Node.js backend to FastAPI)
```json
{
  "userId": 123,
  "topicId": 42,
  "difficulty": "Beginner",
  "message": "Start a scenario about environmental policies."
}
```

### Output (From FastAPI back to Node.js)
```json
{
  "ai_message": "Here is your training scenario...",
  "structured_data": {
    "practiceContent": {
      "topicId": 42,
      "difficulty": "Beginner",
      "generatedBy": "gpt-4o-mini",
      "content": {
        "scenario": "...scenario text..."
      }
    },
    "usage": {
      "prompt_tokens": 200,
      "completion_tokens": 400,
      "totalTokens": 600,
      "totalPrompts": 1,
      "estimated_cost_usd": 0.003,
      "model": "gpt-4o-mini"
    }
  }
}
```

### Prisma Mapping:
1. **`PracticeContent` Table:** Insert a new row using the `structured_data.practiceContent` object. This time, the `difficulty` field MUST use the exact string returned (e.g., `"Beginner"`, `"Intermediate"`, or `"Advanced"`).
2. **`AiUsageLog` / `UserUsage` Table:** Same as above. Grab the `usage` object, record the tokens and cost, and set `endpointUsed` to `"/training/generate"`.

---

## 3. Tracking User Attempts

When a user actually types an answer or interacts with the generated scenario, the AI is no longer grading their back-and-forth arguments directly. All you need to do is log what they did.

### Prisma Mapping:
1. **`PracticeAttempt` Table:** Create a new row.
   * `practiceContentId`: Link this to the ID of the `PracticeContent` we just saved in step 1 or 2.
   * `answer`: Save the raw text prompt the user typed (e.g., *"I struggle to explain the economic side of things..."*).
   * `score`: Leave this as `null`.

---
