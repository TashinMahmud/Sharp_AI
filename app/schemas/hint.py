"""Hint generation schemas."""

from typing import List

from pydantic import BaseModel


class HintRequest(BaseModel):
    """Request schema for hint generation."""

    question: str
    arguments: List[str]


class HintResponse(BaseModel):
    """Response schema for hint."""

    hint: str
