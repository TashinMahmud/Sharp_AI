from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Category(BaseModel):
    category_id: str
    user_id: str
    category_name: str
    created_at: Optional[datetime] = None


class CategoryCreate(BaseModel):
    user_id: str
    category_name: str


class CategoryResponse(BaseModel):
    category_id: str
    category_name: str
    created_at: datetime
    topic_count: int = 0
