from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class TrainingMaterial(BaseModel):
    material_id: int
    user_id: int
    topic_id: int
    main_arguments: List[str]
    counter_arguments: List[str]
    rebuttals: List[str]
    difficulty: int
    created_at: Optional[datetime] = None


class MaterialGenerate(BaseModel):
    user_id: int
    topic_id: int
    topic_name: str
    description: Optional[str] = None
    difficulty: int = 3


class MaterialResponse(BaseModel):
    material_id: int
    topic_id: int
    main_arguments: List[str]
    counter_arguments: List[str]
    rebuttals: List[str]
    difficulty: int
    created_at: datetime
