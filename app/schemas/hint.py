from pydantic import BaseModel, ConfigDict, Field
from app.schemas.usage import UsageStats

from typing import Literal

class HintRequest(BaseModel):
    category: str = Field(..., min_length=1, max_length=100)
    title: str = Field(..., min_length=1, max_length=200)
    materials: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1, max_length=2000)
    difficulty: Literal["Beginner", "Intermediate", "Advanced"]

class StructuredData(BaseModel):
    model_config = ConfigDict(extra="ignore")
    usage: UsageStats

class HintResponse(BaseModel):
    hint: str = Field(..., min_length=1)
    structured_data: StructuredData
