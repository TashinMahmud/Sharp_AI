"""Argument generation schemas."""

from typing import List, Literal

from pydantic import BaseModel, Field

Difficulty = Literal["easy", "medium", "hard"]


class GenerateRequest(BaseModel):
    """Request schema for argument generation."""

    topic: str = Field(..., min_length=1, max_length=500)
    difficulty: Difficulty


class ArgumentResponse(BaseModel):
    """Response schema for generated arguments."""

    main_arguments: List[str]
    counter_arguments: List[str]
    rebuttals: List[str]
