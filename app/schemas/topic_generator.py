
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from app.schemas.usage import UsageStats


class TopicGenerateRequest(BaseModel):
    userId: int
    topicId: int
    message: str = Field(..., min_length=1, max_length=2000)


class PracticeContentData(BaseModel):
    topicId: int
    difficulty: Optional[str] = None
    generatedBy: str = "gpt-4o-mini"

class StructuredData(BaseModel):
    model_config = ConfigDict(extra="ignore")

    practiceContent: PracticeContentData
    usage: UsageStats

class TopicGenerateResponse(BaseModel):
    ai_message: str = Field(..., min_length=1)
    structured_data: StructuredData
