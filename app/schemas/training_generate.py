from typing import Literal
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.usage import UsageStats

class TrainingRequest(BaseModel):
    category: str = Field(..., min_length=1, max_length=100)
    title: str = Field(..., min_length=1, max_length=200)
    materials: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1, max_length=2000)
    difficulty: Literal["Beginner", "Intermediate", "Advanced"]

class StructuredData(BaseModel):
    model_config = ConfigDict(extra="ignore")
    usage: UsageStats

class TrainingResponse(BaseModel):
    category: str
    title: str
    difficulty: Literal["Beginner", "Intermediate", "Advanced"]
    ai_message: str = Field(..., min_length=1)
    evaluation: str
    score: float
    structured_data: StructuredData
