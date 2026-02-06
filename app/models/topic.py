from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Topic(BaseModel):
    topic_id: str
    user_id: str
    category_id: str
    topic_name: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None


class TopicCreate(BaseModel):
    user_id: str
    category_id: str
    topic_name: str
    description: Optional[str] = None


class TopicResponse(BaseModel):
    topic_id: str
    topic_name: str
    description: Optional[str]
    category_id: str
    created_at: datetime
    has_materials: bool = False
