from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Progress(BaseModel):
    user_id: int
    topic_id: int
    topic_name: str
    score: float
    difficulty: int
    timestamp: datetime = Field(default_factory=datetime.now)

class ProgressCreate(BaseModel):
    user_id: int
    topic_id: int
    topic_name: str
    score: float
    difficulty: int

class ProgressStats(BaseModel):
    total_quizzes: int
    correct_answers: int
    win_rate: float
    topics_practiced: int
