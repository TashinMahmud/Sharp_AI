import logging
import uuid
from datetime import datetime
from typing import List, Dict, Any
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

from app.core.config import get_settings
from app.models.progress import Progress, ProgressCreate, ProgressStats

logger = logging.getLogger(__name__)

class ProgressService:
    _instance = None

    def __init__(self):
        try:
            self.settings = get_settings()
            self.embeddings = OpenAIEmbeddings(
                api_key=self.settings.openai_api_key,
                model="text-embedding-3-small"
            )
            
            logger.info(f"Initializing ProgressService with ChromaDB at {self.settings.chroma_path}")
            self.vector_db = Chroma(
                persist_directory=self.settings.chroma_path,
                embedding_function=self.embeddings,
                collection_name="user_progress"
            )
        except Exception as e:
            logger.error(f"Failed to initialize ProgressService: {e}")
            raise

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def save_quiz_result(self, data: ProgressCreate) -> bool:
        try:
            progress_id = str(uuid.uuid4())
            metadata = {
                "progress_id": progress_id,
                "user_id": data.user_id,
                "topic_id": data.topic_id,
                "topic_name": data.topic_name,
                "score": data.score,
                "difficulty": data.difficulty,
                "timestamp": datetime.now().isoformat(),
                "type": "progress"
            }
            
            # We store a simple text representation for potential semantic search later
            text_content = f"Quiz Result: {data.topic_name} - {'Correct' if data.score == 1 else 'Incorrect'}"
            
            self.vector_db.add_texts(
                texts=[text_content],
                metadatas=[metadata],
                ids=[progress_id]
            )
            logger.info(f"Saved progress for user {data.user_id} on topic {data.topic_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to save progress: {e}")
            return False

    def get_user_stats(self, user_id: str) -> ProgressStats:
        try:
            results = self.vector_db.get(
                where={
                    "$and": [
                        {"user_id": {"$eq": user_id}},
                        {"type": {"$eq": "progress"}}
                    ]
                },
                include=["metadatas"]
            )
            
            total_quizzes = 0
            correct_answers = 0
            topics_practiced = set()
            
            if results and results["metadatas"]:
                for meta in results["metadatas"]:
                    total_quizzes += 1
                    if meta.get("score") == 1:
                        correct_answers += 1
                    topics_practiced.add(meta.get("topic_id"))
            
            win_rate = (correct_answers / total_quizzes * 100) if total_quizzes > 0 else 0.0
            
            return ProgressStats(
                total_quizzes=total_quizzes,
                correct_answers=correct_answers,
                win_rate=round(win_rate, 2),
                topics_practiced=len(topics_practiced)
            )
        except Exception as e:
            logger.error(f"Failed to get stats for user {user_id}: {e}")
            return ProgressStats(total_quizzes=0, correct_answers=0, win_rate=0.0, topics_practiced=0)

    def delete_user_progress(self, user_id: str) -> int:
        try:
            results = self.vector_db.get(
                where={
                    "$and": [
                        {"user_id": {"$eq": user_id}},
                        {"type": {"$eq": "progress"}}
                    ]
                },
                include=["metadatas"]
            )
            
            if results and results["ids"]:
                ids_to_delete = results["ids"]
                self.vector_db.delete(ids=ids_to_delete)
                logger.info(f"Deleted {len(ids_to_delete)} progress records for user {user_id}")
                return len(ids_to_delete)
            return 0
        except Exception as e:
            logger.error(f"Failed to delete progress for user {user_id}: {e}")
            return 0

def get_progress_service() -> ProgressService:
    return ProgressService.get_instance()
