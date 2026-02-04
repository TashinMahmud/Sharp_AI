"""Debate chat schemas."""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from app.schemas.argument import Difficulty


DebateRole = Literal["user_argument", "user_counter", "user_rebuttal"]
AIRole = Literal["counter_argument", "rebuttal", "challenge"]


class DebateTurn(BaseModel):
    """Single turn in the debate history."""

    role: str = Field(..., min_length=1, max_length=50)
    message: str = Field(..., min_length=1, max_length=2000)


class DebateChatRequest(BaseModel):
    """Request schema for a single debate chat turn."""

    topic: str = Field(..., min_length=1, max_length=500)
    difficulty: Difficulty
    role: DebateRole
    message: str = Field(..., min_length=1, max_length=2000)
    debate_history: Optional[List[DebateTurn]] = None


class DebateChatResponse(BaseModel):
    """Response schema for a single debate chat turn."""

    ai_role: AIRole
    ai_message: str = Field(..., min_length=1, max_length=2000)

