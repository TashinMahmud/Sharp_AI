# ⚡ Sharp AI Core Engine

This document defines the 3 primary stateless endpoints used by the Sharp AI engine.
Everything is deployed and accessible at the base URL: `http://46.62.216.255/ai`

---

## 🗣️ Training Endpoints

These are the primary routes for the actual chat interface where the user debates the AI.

### `POST /training/generate`
Starts or continues a debate scenario based on difficulty parameters.

**Request Body:**
```json
{
  "title": "string",
  "difficulty": "Beginner",
  "message": "string"
}
```

**Response:**
```json
{
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
  "title": "Universal Basic Income",
  "difficulty": "Beginner",
  "message": "UBI will cause massive inflation because people will just spend the free money."
}
```

**Example Response:**
```json
{
  "ai_message": "### 1. Answer\nThat is a common misconception, but giving people a safety net actually stimulates local economies...\n\n### 2. Data / Facts\n- A 2021 study showed UBI recipients increased local spending by 15%.\n- Inflation rates in pilot cities remained strictly in line with national averages.\n\n### 3. Studies\n- Stockton Economic Empowerment Demonstration (SEED) report.\n\n### 4. Dodge Counter\nPeople say: \"Free money just devalues the currency.\" But just like adding oil to an engine doesn't destroy the car, injecting capital into the base economy lubricates the machine.",
  "structured_data": {
    "usage": {
      "prompt_tokens": 402,
      "completion_tokens": 150,
      "totalTokens": 552,
      "totalPrompts": 1,
      "estimated_cost_usd": 0.00015,
      "model": "gpt-4o-mini"
    }
  }
}
```

### `POST /training/hint`
Acts as a stealth coach, providing a 1-sentence strategic hint on how to counter a specific opponent's message.

**Request Body:**
```json
{
  "title": "string",
  "message": "string"
}
```

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
  "title": "Universal Basic Income",
  "message": "The opponent said UBI disincentivizes work."
}
```

**Example Response:**
```json
{
  "hint": "Try pointing out studies that show UBI actually empowers people to seek better employment or start small businesses rather than quitting work altogether.",
  "structured_data": {
    "usage": {
      "prompt_tokens": 120,
      "completion_tokens": 25,
      "totalTokens": 145,
      "totalPrompts": 1,
      "estimated_cost_usd": 0.00003,
      "model": "gpt-4o-mini"
    }
  }
}
```

---

## 📚 Topics Endpoints

### `POST /topics/generate`
Have the AI dynamically formulate a structured 4-part argument Topic Card based purely on a user description or idea.

**Request Body:**
```json
{
  "title": "string",
  "description": "string"
}
```

**Response:**
```json
{
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
  "title": "Climate Change Policy",
  "description": "A debate about whether strict emissions regulations are hurting the economy."
}
```

**Example Response:**
```json
{
  "ai_message": "### 1. Answer\nStrict regulations often cripple local industries and ship jobs overseas where environmental laws don't exist...\n\n### 2. Data / Facts\n- The proposed carbon tax would eliminate an estimated 1.4 million manufacturing jobs by 2030.\n- Global emissions from un-regulated countries outpace western reductions by 12 to 1.\n\n### 3. Studies\n- Heritage Foundation analysis on the economic cost of strict carbon caps.\n\n### 4. Dodge Counter\nPeople say: \"We must regulate to save our children's future.\" But burning our own house down to stay warm isn't a workable strategy; we need innovation-driven solutions, not economy-crushing regulations.",
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
