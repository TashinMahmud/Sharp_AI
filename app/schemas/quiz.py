"""Quiz generation schemas."""

from typing import List

from pydantic import BaseModel, Field

from app.schemas.argument import Difficulty


class QuizRequest(BaseModel):
    """Request schema for quiz generation."""

    topic: str = Field(..., min_length=1, max_length=500)
    difficulty: Difficulty
    arguments: List[str] = Field(..., min_length=1)


class QuizResponse(BaseModel):
    """Response schema for quiz question."""

    question: str
    options: List[str]
    correct_answer: int
    explanation: str
