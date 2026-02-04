"""Pydantic schemas for request/response validation."""

from app.schemas.argument import ArgumentResponse, Difficulty, GenerateRequest
from app.schemas.debate_chat import (
    AIRole,
    DebateChatRequest,
    DebateChatResponse,
    DebateRole,
    DebateTurn,
)
from app.schemas.evaluate import EvaluateRequest, EvaluateResponse
from app.schemas.hint import HintRequest, HintResponse
from app.schemas.quiz import QuizRequest, QuizResponse

__all__ = [
    "Difficulty",
    "GenerateRequest",
    "ArgumentResponse",
    "QuizRequest",
    "QuizResponse",
    "HintRequest",
    "HintResponse",
    "EvaluateRequest",
    "EvaluateResponse",
    "DebateRole",
    "AIRole",
    "DebateTurn",
    "DebateChatRequest",
    "DebateChatResponse",
]
