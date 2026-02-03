"""Answer evaluation schemas."""

from pydantic import BaseModel, Field

from app.schemas.argument import Difficulty


class EvaluateRequest(BaseModel):
    """Request schema for answer evaluation."""

    question: str = Field(..., min_length=1, max_length=2000)
    selected_answer: str = Field(..., min_length=1, max_length=1000)
    correct_answer: str = Field(..., min_length=1, max_length=1000)
    difficulty: Difficulty


class EvaluateResponse(BaseModel):
    """Response schema for evaluation feedback."""

    feedback: str
