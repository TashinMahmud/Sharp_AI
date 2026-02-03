"""Pydantic schemas for request/response validation."""

from app.schemas.argument import ArgumentResponse, GenerateRequest
from app.schemas.evaluate import EvaluateRequest, EvaluateResponse
from app.schemas.hint import HintRequest, HintResponse
from app.schemas.quiz import QuizRequest, QuizResponse

__all__ = [
    "GenerateRequest",
    "ArgumentResponse",
    "QuizRequest",
    "QuizResponse",
    "HintRequest",
    "HintResponse",
    "EvaluateRequest",
    "EvaluateResponse",
]
