
from typing import List, Literal, Optional, Dict, Any

from pydantic import BaseModel, Field


from app.schemas.usage import UsageStats


DebateRole = Literal["argument", "counter_argument", "rebuttal"]
AIRole = Literal["counter_argument", "rebuttal", "challenge"]


class DebateTurn(BaseModel):

    role: str = Field(..., min_length=1, max_length=50)
    message: str = Field(..., min_length=1, max_length=2000)


class DebateChatRequest(BaseModel):

    topicId: int
    userId: int
    difficulty: int = Field(..., ge=1, le=5)
    userRole: DebateRole
    message: str = Field(..., min_length=1, max_length=2000)
    debate_history: Optional[List[DebateTurn]] = None
    session_id: Optional[str] = Field(None, min_length=1, max_length=255)


class PracticeContentData(BaseModel):
    topicId: int
    difficulty: int
    generatedBy: str = "gpt-4o-mini"

class PracticeAttemptData(BaseModel):
    userId: int
    score: float

class StructuredData(BaseModel):
    practiceContent: PracticeContentData
    practiceAttempt: PracticeAttemptData
    usage: UsageStats

class DebateChatResponse(BaseModel):
    ai_message: str = Field(..., min_length=1)
    structured_data: StructuredData
