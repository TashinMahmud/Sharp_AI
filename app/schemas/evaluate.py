
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.argument import Difficulty


class EvaluateRequest(BaseModel):

    question: str = Field(..., min_length=1, max_length=2000)
    selected_answer: str = Field(..., min_length=1, max_length=1000)
    correct_answer: str = Field(..., min_length=1, max_length=1000)
    difficulty: Difficulty
    user_id: Optional[str] = Field(None, min_length=1, max_length=255)
    session_id: Optional[str] = Field(None, min_length=1, max_length=255)


class EvaluateResponse(BaseModel):

    feedback: str
