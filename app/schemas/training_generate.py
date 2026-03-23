
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.usage import UsageStats


class TrainingRequest(BaseModel):
    userId: int
    topicId: int
    difficulty: Literal["Beginner", "Intermediate", "Advanced"]
    message: str = Field(..., min_length=1, max_length=2000)


class PracticeContentData(BaseModel):
    topicId: int
    difficulty: Optional[str] = None
    generatedBy: str = "gpt-4o-mini"

class StructuredData(BaseModel):
    model_config = ConfigDict(extra="ignore")

    practiceContent: PracticeContentData
    usage: UsageStats

class TrainingResponse(BaseModel):
    ai_message: str = Field(..., min_length=1)
    structured_data: StructuredData
