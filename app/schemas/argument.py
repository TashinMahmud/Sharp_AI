
from typing import List, Literal, Optional, Dict, Any

from pydantic import BaseModel, Field



from app.schemas.usage import UsageStats


class GenerateRequest(BaseModel):

    topicId: int
    userId: int
    difficulty: int = Field(..., ge=1, le=5)
    session_id: Optional[str] = Field(None, min_length=1, max_length=255)


class ArgumentResponse(BaseModel):

    content: Dict[str, Any]
    generatedBy: str = "gpt-4o-mini"
    usage: Optional[UsageStats] = None
