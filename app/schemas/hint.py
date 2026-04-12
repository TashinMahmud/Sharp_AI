from pydantic import BaseModel, ConfigDict, Field
from app.schemas.usage import UsageStats

class HintRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    message: str = Field(..., min_length=1, max_length=2000)

class StructuredData(BaseModel):
    model_config = ConfigDict(extra="ignore")
    usage: UsageStats

class HintResponse(BaseModel):
    hint: str = Field(..., min_length=1)
    structured_data: StructuredData
