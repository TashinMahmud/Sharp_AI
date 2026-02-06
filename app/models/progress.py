from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Progress(BaseModel):
    user_id: str
    topic_id: str
    topic_name: str
    score: int  # 1 for correct, 0 for incorrect
    difficulty: str
    timestamp: datetime = Field(default_factory=datetime.now)

class ProgressCreate(BaseModel):
    user_id: str
    topic_id: str
    topic_name: str
    score: int
    difficulty: str

class ProgressStats(BaseModel):
    total_quizzes: int
    correct_answers: int
    win_rate: float
    topics_practiced: int
