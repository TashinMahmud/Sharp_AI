from pydantic import BaseModel, ConfigDict, Field
from app.schemas.usage import UsageStats

class TopicGenerateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: str = Field(..., min_length=1, max_length=2000)

class StructuredData(BaseModel):
    model_config = ConfigDict(extra="ignore")
    usage: UsageStats

class TopicGenerateResponse(BaseModel):
    ai_message: str = Field(..., min_length=1)
    structured_data: StructuredData
