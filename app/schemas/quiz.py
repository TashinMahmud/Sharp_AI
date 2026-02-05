
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.argument import Difficulty


class QuizRequest(BaseModel):

    topic: str = Field(..., min_length=1, max_length=500)
    difficulty: Difficulty
    arguments: List[str] = Field(..., min_length=1)
    user_id: Optional[str] = Field(None, min_length=1, max_length=255)
    session_id: Optional[str] = Field(None, min_length=1, max_length=255)


class QuizResponse(BaseModel):

    question: str
    options: List[str]
    correct_answer: int
    explanation: str
