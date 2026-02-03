"""Answer evaluation schemas."""

from pydantic import BaseModel


class EvaluateRequest(BaseModel):
    """Request schema for answer evaluation."""

    question: str
    selected_answer: str
    correct_answer: str
    difficulty: str


class EvaluateResponse(BaseModel):
    """Response schema for evaluation feedback."""

    feedback: str
