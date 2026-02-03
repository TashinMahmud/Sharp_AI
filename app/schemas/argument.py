"""Argument generation schemas."""

from typing import List

from pydantic import BaseModel


class GenerateRequest(BaseModel):
    """Request schema for argument generation."""

    topic: str
    difficulty: str


class ArgumentResponse(BaseModel):
    """Response schema for generated arguments."""

    main_arguments: List[str]
    counter_arguments: List[str]
    rebuttals: List[str]
