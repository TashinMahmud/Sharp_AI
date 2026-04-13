from pydantic import BaseModel, ConfigDict, Field
from app.schemas.usage import UsageStats

class TopicGenerateRequest(BaseModel):
    category: str = Field(..., min_length=1, max_length=100)
    message: str = Field(..., min_length=1, max_length=2000)

class StructuredData(BaseModel):
    model_config = ConfigDict(extra="ignore")
    usage: UsageStats

class TopicGenerateResponse(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    ai_message: str = Field(..., min_length=1)
    structured_data: StructuredData
