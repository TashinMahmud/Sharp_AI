
from typing import List, Literal, Optional

from pydantic import BaseModel, Field

Difficulty = Literal["easy", "medium", "hard"]


class GenerateRequest(BaseModel):

    topic: str = Field(..., min_length=1, max_length=500)
    difficulty: Difficulty
    user_id: Optional[str] = Field(None, min_length=1, max_length=255)
    session_id: Optional[str] = Field(None, min_length=1, max_length=255)


class ArgumentResponse(BaseModel):

    main_arguments: List[str]
    counter_arguments: List[str]
    rebuttals: List[str]
