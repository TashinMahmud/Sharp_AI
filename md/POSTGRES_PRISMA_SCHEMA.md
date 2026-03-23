# Suggested PostgreSQL Prisma Schema

This is the recommended `schema.prisma` file that your Main Backend team should use to perfectly integrate with the FastAPI AI Engine. 

Since the FastAPI Python engine returns perfectly typed JSON, your backend can just take those JSON responses and funnel them straight into these Prisma models!

```prisma
// schema.prisma

generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

// ----------------------------------------------------
// 1. Core Models (Users, Categories, Topics)
// ----------------------------------------------------

model User {
  id               Int                @id @default(autoincrement())
  email            String             @unique
  name             String?
  createdAt        DateTime           @default(now())
  
  // Relations
  categories       Category[]
  topics           Topic[]
  practiceAttempts PracticeAttempt[]
  materials        TrainingMaterial[]
}

model Category {
  id            Int      @id @default(autoincrement()) // Matches typical FastAPI 'category_id'
  userId        Int
  categoryName  String
  description   String?
  createdAt     DateTime @default(now())

  // Relations
  user          User     @relation(fields: [userId], references: [id], onDelete: Cascade)
  topics        Topic[]

  @@index([userId])
}

model Topic {
  id            Int      @id @default(autoincrement()) // Matches typical FastAPI 'topic_id'
  userId        Int
  categoryId    Int?
  topicName     String
  description   String?
  createdAt     DateTime @default(now())

  // Relations
  user          User       @relation(fields: [userId], references: [id], onDelete: Cascade)
  category      Category?  @relation(fields: [categoryId], references: [id], onDelete: SetNull)
  materials     TrainingMaterial[]
  practiceAttempts PracticeAttempt[]

  @@index([userId])
  @@index([categoryId])
}

// ----------------------------------------------------
// 2. Training Material (AI Generated Output)
// ----------------------------------------------------

model TrainingMaterial {
  id          Int      @id @default(autoincrement()) // Matches FastAPI 'material_id'
  userId      Int
  topicId     Int
  difficulty  Int      // 1-5 scale (matches FastAPI)
  generatedBy String   // Usually "gpt-4o-mini"
  content     Json     // Store the {"main_arguments": [], "counter_arguments": [], "rebuttals": []} object here
  createdAt   DateTime @default(now())

  // Relations
  user        User     @relation(fields: [userId], references: [id], onDelete: Cascade)
  topic       Topic    @relation(fields: [topicId], references: [id], onDelete: Cascade)

  @@index([topicId])
  @@index([userId])
}

// ----------------------------------------------------
// 3. User Progress & Attempts (Quizzes / Debates)
// ----------------------------------------------------

model PracticeAttempt {
  id                Int      @id @default(autoincrement())
  userId            Int
  topicId           Int
  score             Float    // Matches FastAPI evaluated float score (e.g., 0.85)
  difficulty        Int      // The difficulty level practiced (1-5)
  attemptType       String   // e.g., "QUIZ" or "DEBATE"
  sessionId         String?  // Optional: Links back to the session_id used in the FastAPI debate
  timestamp         DateTime @default(now())

  // Relations
  topic             Topic    @relation(fields: [topicId], references: [id], onDelete: Cascade)
  user              User     @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@index([userId])
  @@index([topicId])
}

// ----------------------------------------------------
// 4. Usage Tracking (Cost Management)
// ----------------------------------------------------

model AiUsageLog {
  id                 Int      @id @default(autoincrement())
  userId             Int
  endpointUsed       String   // e.g., "/training/debate"
  model              String   // e.g., "gpt-4o-mini"
  promptTokens       Int
  completionTokens   Int
  totalTokens        Int
  totalPrompts       Int      // Important metric returning from FastAPI
  estimatedCostUsd   Float    // The calculated cost returned by FastAPI
  timestamp          DateTime @default(now())

  @@index([userId])
}
```

### How to use this schema:
Every time the Next.js / Node.js backend receives a JSON response from the Python FastAPI server, they just run standard Prisma Create commands. 

For example, when `POST /topics/{topic}/generate-materials` finishes:
```javascript
// Example Next.js/Prisma code handling the FastAPI response
const fastApiResponse = await fetch("http://fastapi:8000/topics/123/generate-materials", ...);
const data = await fastApiResponse.json();

await prisma.trainingMaterial.create({
  data: {
    userId: data.user_id,
    topicId: data.topic_id,
    difficulty: data.difficulty,
    generatedBy: data.generatedBy,
    content: data.content // Safely inject the highly layered Argument/Rebuttal JSON array here!
  }
});
```
