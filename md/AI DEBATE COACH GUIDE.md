# How the AI Debate Coach Works

*A Guide for Non-Technical Users*

Imagine our AI Debate Coach as a **Harvard-tier debate strategist** sitting across from the user. It doesn't just chat; it studies the material, remembers everything the user says, counters with hard facts, and silently grades their performance.

Here is exactly how this intelligent engine operates, step-by-step:

---

## Pillar 1: The "Textbook" (State Preparation)

Before the debate even begins, the AI asks: *"What are we arguing about, and what are the ground rules?"*

**The Analogy:** You wouldn't walk into a debate tournament without studying. Neither does the AI. Before the user says a single word, the backend automatically hands the AI the "Textbook" — a collection of arguments, counterarguments, and facts specific to the chosen topic (like *Universal Basic Income*). The AI reads this textbook instantly, ensuring it stays relentlessly on topic and only debates relevant facts.

---

## Pillar 2: The "4-Part Punch" (Response Structure)

Most chatbots ramble indefinitely. The AI Debate Coach is trained to hit back with the **clinical precision of a professional debater**. Every single time the AI speaks, it forces its thoughts into exactly four highly readable sections.

**Example User Message:**
> "Universal Basic Income (UBI) is complete nonsense. It will cost the government trillions of dollars we don't have, causing massive inflation."

**The AI's 4-Part Punch:**

1. **The Direct Answer** *(The immediate punch back)*
   > "While inflation is a concern, ignoring the crushing reality of poverty costs the government significantly more long-term."

2. **The Data / Facts** *(The receipts)*
   - "A Roosevelt Institute study showed UBI could actually grow the US economy by $2.5 trillion by 2025 by stimulating consumer spending."
   - "Childhood poverty currently costs the US over $1 trillion annually in lost productivity and increased healthcare costs."

3. **The Studies** *(The academic backing)*
   - According to the 2021 Stockton Economic Empowerment Demonstration (SEED).

4. **The Dodge Counter** *(The pivot and analogy)*
   > "People say: giving away free money causes inflation. But arguing that we can't afford a safety net while the ship is actively sinking is like complaining about the cost of life vests while drowning; UBI is the life raft the middle class needs today."

By strictly enforcing this format, the user's screen stays **clean, sharp, and easy to read**.

---

## Pillar 3: The "Secret Filing Cabinet" (Long-Term Memory)

If you talk to ChatGPT, it forgets what you said 20 minutes ago. Our Debate Coach has a **"Secret Filing Cabinet"** dedicated exactly to the current user.

**The Analogy:** Imagine a fast-paced debate on Healthcare.

- **Message 1:** The user argues that universal healthcare is too expensive. The AI counters.
- **Message 5:** The user tries to change the subject, arguing that Canada has longer wait times for doctors.

Instead of just answering the Canada question, the AI opens its Filing Cabinet, pulls out Message 1, and synthesizes them:

> *"You mentioned earlier that cost was your primary concern, but now you are pivoting to wait times. Let's look at the facts: Canadians spend roughly half of what Americans spend per capita on healthcare, and their wait times for emergency triage are virtually identical."*

The AI doesn't just respond; it **actively remembers** the user's past logic and holds them accountable to their own previous statements.

---

## Pillar 4: The "Invisible Grader" (Objective Scoring)

The user never sees this happening during the debate, but it is the **most valuable part** of the platform.

**The Analogy:** Imagine a silent judge standing behind the debate podium with a clipboard. Every time the user sends a message, this judge gives them a grade from **0 to 100** based on:

- Did their argument make **logical sense**?
- Did they actually use **facts**, or just emotions?
- Did they use strong **debate vocabulary**?

While the user is busy reading the "4-Part Punch", the AI secretly hands your database a score (for example: `0.82`, meaning an **82%**).

Your database saves that number. Later, the user can go to their profile dashboard and see beautiful charts proving they are getting better, saying:
- *"Your debate consistency improved by 15% this week!"*
- *"You scored an 88% against the Conservative Persona on Nuclear Energy."*

---

## Summary of the Flow

1. **User picks a topic.** → The AI reads the Textbook.
2. **User makes a point.** → The AI checks the Filing Cabinet to remember past points.
3. **The AI hits back** using the 4-Part Punch (Answer, Data, Studies, Dodge).
4. **The Invisible Grader** secretly scores the user's logic and sends it to the central database to track their progress over time.

---

---

# The Input and Output

## What the Frontend Sends to the Main Backend

The Frontend will make an HTTP `POST` request to the Main Backend with this JSON:

```json
{
  "userId": 104,
  "topicId": 248813158,
  "role": "argument",
  "message": "Universal Basic Income is a terrible idea because it causes inflation."
}
```

### Breakdown of the 4 Fields:

| Field | Type | Description |
|-------|------|-------------|
| `userId` | Integer | The ID of the logged-in user. The Frontend gets this from their session or JWT auth token. |
| `topicId` | Integer | The database ID of the topic they are currently debating. The Frontend knows this because they clicked on that specific topic. |
| `role` | String | Which "side" of the debate the user is on. Valid options: `"argument"`, `"counter_argument"`, or `"rebuttal"`. |
| `message` | String | The literal text string the user typed into the chat box. |

---

## What the Main Backend Sends to FastAPI

The Main Backend (Node.js) attaches `sessionId` and `difficulty`, then forwards to FastAPI:

```json
{
  "userId": 104,
  "sessionId": "debate-session-99281a",
  "topicId": 248813158,
  "difficulty": 4,
  "role": "argument",
  "message": "Universal Basic Income is a terrible idea because it causes inflation."
}
```

### Breakdown of the 6 Fields:

| Field | Type | Description |
|-------|------|-------------|
| `userId` | Int | Tells the AI *who* is talking, so it knows whose "Secret Filing Cabinet" (memory) to look inside. |
| `sessionId` | String | Groups the messages together. A new `sessionId` means a fresh conversation. |
| `topicId` | Int | Tells the AI which "Textbook" of facts to pull before it argues. |
| `difficulty` | Int (1-5) | Tells the AI how merciless to be. `1` = simple concepts. `5` = advanced macroeconomic theory. |
| `role` | String | The user's stance. Valid options: `"argument"`, `"counter_argument"`, or `"rebuttal"`. |
| `message` | String | The actual text the user typed on the screen. |

---

## What FastAPI Returns

FastAPI returns a perfectly structured JSON object:

```json
{
  "ai_message": "### 1. Answer\nWhile I hear your point on UBI, you are ignoring the massive inflationary pressure...",
  "structured_data": {
    "practiceContent": {
      "topicId": 248813158,
      "difficulty": 4,
      "generatedBy": "gpt-4o-mini"
    },
    "practiceAttempt": {
      "userId": 104,
      "score": 0.85
    },
    "usage": {
      "prompt_tokens": 1053,
      "completion_tokens": 289,
      "totalTokens": 1342,
      "totalPrompts": 1,
      "estimated_cost_usd": 0.00033135
    }
  }
}
```

---

## The Full Cycle (Frontend ➡ Backend ➡ FastAPI)

1. **The User** types: *"UBI causes inflation!"* and hits Send on the React frontend.
2. **The Main Backend (Node.js)** receives that text, attaches the user's ID and current topic, and sends the 6-field JSON payload above to our FastAPI server.
3. **FastAPI** does all the heavy lifting (RAG, ChromaDB, OpenAI, formatting).
4. **FastAPI** returns the massive JSON with the graded `score`, `usage` costs, and the 4-part Markdown `ai_message`.
5. **The Main Backend** saves the score to the DB and forwards the 4-part Markdown string back to the React frontend to display on the screen!

---

---

# Other Endpoint Input/Output Reference

## 1. Create a Category

**`POST /categories`** — Creates a top-level folder for topics.

**Input JSON:**
```json
{
  "user_id": 104,
  "category_name": "Economics"
}
```

**Output JSON:**
```json
{
  "category_id": 1368958949,
  "category_name": "Economics",
  "created_at": "2024-03-08T15:30:00Z",
  "topic_count": 0
}
```

---

## 2. Create a Topic

**`POST /topics`** — Adds a specific topic inside a category. *(This also auto-generates study materials simultaneously in the background!)*

**Input JSON:**
```json
{
  "user_id": 104,
  "category_id": 1368958949,
  "topic_name": "Universal Healthcare",
  "description": "The economic impact of universal healthcare."
}
```
> **Note:** `category_id` and `description` are optional.

**Output JSON:**
```json
{
  "topic_id": 248813158,
  "topic_name": "Universal Healthcare",
  "description": "The economic impact of universal healthcare.",
  "category_id": 1368958949,
  "created_at": "2024-03-08T15:35:00Z",
  "has_materials": false
}
```

---

## 3. Generate Study Materials (Manual)

**`POST /materials/generate`** — Triggers the AI to research the topic and build the "Textbook" of arguments. *(Usually this runs automatically when a Topic is created, but you can trigger it manually here.)*

**Input JSON:**
```json
{
  "topicId": 248813158,
  "userId": 104
}
```

**Output JSON:**
```json
{
  "material_id": 5991823,
  "topic_id": 248813158,
  "main_arguments": ["Healthcare is a human right", "Reduces long term costs"],
  "counter_arguments": ["Taxes will increase", "Wait times may rise"],
  "rebuttals": ["Taxes offset insurance premiums", "Triage handles emergencies"],
  "difficulty": 3,
  "created_at": "2024-03-08T15:36:00Z"
}
```

---

## 4. Pull the Topic's Study Materials

**`GET /topics/{topic_id}/materials`** — Retrieves the auto-generated study materials for a topic.

**Input:** No JSON body. Just pass the `topic_id` in the URL.

**Output JSON:**
```json
{
  "material_id": 5991823,
  "topic_id": 248813158,
  "main_arguments": [
    "UBI guarantees a safety net for all citizens",
    "It stimulates the local economy through direct spending",
    "It reduces the bureaucratic cost of means-tested welfare",
    "It provides financial security during technological job displacement",
    "It empowers workers to negotiate better wages and conditions"
  ],
  "counter_arguments": [
    "UBI could trigger massive systemic inflation",
    "It is incredibly expensive and expands the national deficit",
    "It might disincentivize labor participation and work ethic",
    "It is an inefficient use of capital compared to targeted programs",
    "It requires significant, unpopular tax hikes to fund"
  ],
  "rebuttals": [
    "Inflation is primarily driven by supply-chain issues, not consumer demand",
    "Funding can be sourced from wealth taxes, not working-class income",
    "Studies show basic income has negligible negative effects on employment",
    "Universal programs eliminate the 'welfare trap' where people lose benefits for working",
    "The cost of poverty far exceeds the upfront cost of UBI"
  ],
  "difficulty": 3,
  "created_at": "2024-03-08T15:36:00Z"
}
```
