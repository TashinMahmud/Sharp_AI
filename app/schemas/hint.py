
from typing import List, Optional

from pydantic import BaseModel, Field


class HintRequest(BaseModel):

    question: str = Field(..., min_length=1, max_length=2000)
    arguments: List[str] = Field(..., min_length=1)
    user_id: Optional[str] = Field(None, min_length=1, max_length=255)
    session_id: Optional[str] = Field(None, min_length=1, max_length=255)


class HintResponse(BaseModel):

    hint: str
