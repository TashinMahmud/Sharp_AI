"""Hint generation schemas."""

from typing import List

from pydantic import BaseModel, Field


class HintRequest(BaseModel):
    """Request schema for hint generation."""

    question: str = Field(..., min_length=1, max_length=2000)
    arguments: List[str] = Field(..., min_length=1)


class HintResponse(BaseModel):
    """Response schema for hint."""

    hint: str
