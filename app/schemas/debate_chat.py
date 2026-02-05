
from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from app.schemas.argument import Difficulty


DebateRole = Literal["user_argument", "user_counter", "user_rebuttal"]
AIRole = Literal["counter_argument", "rebuttal", "challenge"]


class DebateTurn(BaseModel):

    role: str = Field(..., min_length=1, max_length=50)
    message: str = Field(..., min_length=1, max_length=2000)


class DebateChatRequest(BaseModel):

    topic: str = Field(..., min_length=1, max_length=500)
    difficulty: Difficulty
    role: DebateRole
    message: str = Field(..., min_length=1, max_length=2000)
    debate_history: Optional[List[DebateTurn]] = None
    user_id: Optional[str] = Field(None, min_length=1, max_length=255)
    session_id: Optional[str] = Field(None, min_length=1, max_length=255)


class DebateChatResponse(BaseModel):

    ai_role: AIRole
    ai_message: str = Field(..., min_length=1, max_length=2000)
