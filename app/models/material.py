from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class TrainingMaterial(BaseModel):
    material_id: str
    user_id: str
    topic_id: str
    main_arguments: List[str]
    counter_arguments: List[str]
    rebuttals: List[str]
    difficulty: str
    created_at: Optional[datetime] = None


class MaterialGenerate(BaseModel):
    user_id: str
    topic_id: str
    topic_name: str
    description: Optional[str] = None
    difficulty: str = "medium"


class MaterialResponse(BaseModel):
    material_id: str
    topic_id: str
    main_arguments: List[str]
    counter_arguments: List[str]
    rebuttals: List[str]
    difficulty: str
    created_at: datetime
