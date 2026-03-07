
from typing import List, Optional

from pydantic import BaseModel, Field


from app.schemas.usage import UsageStats


class QuizRequest(BaseModel):

    topicId: int
    userId: int
    practiceContentId: int
    difficulty: int = Field(..., ge=1, le=5)
    arguments: List[str] = Field(..., min_length=1)
    session_id: Optional[str] = Field(None, min_length=1, max_length=255)


class QuizResponse(BaseModel):

    question: str
    options: List[str]
    correct_answer: int
    explanation: str
    usage: Optional[UsageStats] = None
