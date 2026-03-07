
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field

from app.schemas.usage import UsageStats


class EvaluateRequest(BaseModel):

    practiceContentId: int
    userId: int
    question: str = Field(..., min_length=1, max_length=2000)
    selected_answer: str = Field(..., min_length=1, max_length=1000)
    correct_answer: str = Field(..., min_length=1, max_length=1000)
    difficulty: int = Field(..., ge=1, le=5)
    session_id: Optional[str] = Field(None, min_length=1, max_length=255)


class EvaluateResponse(BaseModel):

    score: float
    feedback: str
    answer: Dict[str, Any]
    usage: Optional[UsageStats] = None
