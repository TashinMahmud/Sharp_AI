from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Topic(BaseModel):
    topic_id: int
    user_id: int
    category_id: Optional[int] = None
    topic_name: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None


class TopicCreate(BaseModel):
    user_id: int
    category_id: Optional[int] = None  # Optional - topics can exist without category
    topic_name: str
    description: Optional[str] = None


class TopicResponse(BaseModel):
    topic_id: int
    topic_name: str
    description: Optional[str]
    category_id: Optional[int] = None  # May be null for uncategorized topics
    created_at: datetime
    has_materials: bool = False
