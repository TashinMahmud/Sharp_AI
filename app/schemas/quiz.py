"""Quiz generation schemas."""

from typing import List

from pydantic import BaseModel


class QuizRequest(BaseModel):
    """Request schema for quiz generation."""

    topic: str
    difficulty: str
    arguments: List[str]


class QuizResponse(BaseModel):
    """Response schema for quiz question."""

    question: str
    options: List[str]
    correct_answer: int
    explanation: str
