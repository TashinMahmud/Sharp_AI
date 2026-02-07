import uuid
import logging
from datetime import datetime

from typing import List, Optional



from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

from app.core.config import get_settings
from app.models.topic import Topic, TopicCreate, TopicResponse

logger = logging.getLogger(__name__)


class TopicService:
    _instance = None
    
    def __init__(self):
        try:
            self.settings = get_settings()
            self.embeddings = OpenAIEmbeddings(
                api_key=self.settings.openai_api_key,
                model="text-embedding-3-small"
            )
            
            logger.info(f"Initializing TopicService with ChromaDB at {self.settings.chroma_path}")
            self.vector_db = Chroma(
                persist_directory=self.settings.chroma_path,
                embedding_function=self.embeddings,
                collection_name="user_topics"
            )
        except Exception as e:
            logger.error(f"Failed to initialize TopicService: {e}")
            raise
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def create_topic(self, user_id: str, topic_name: str, category_id: Optional[str] = None, description: Optional[str] = None) -> TopicResponse:
        topic_id = str(uuid.uuid4())
        created_at = datetime.now()
        
        metadata = {
            "topic_id": topic_id,
            "user_id": user_id,
            "category_id": category_id,
            "topic_name": topic_name,
            "description": description or "",
            "created_at": created_at.isoformat(),
            "type": "topic"
        }
        
        text_content = f"Topic: {topic_name}"
        if description:
            text_content += f" - {description}"
        
        self.vector_db.add_texts(
            texts=[text_content],
            metadatas=[metadata],
            ids=[topic_id]
        )
        
        logger.info(f"Created topic {topic_id} in category {category_id} for user {user_id}")
        
        return TopicResponse(
            topic_id=topic_id,
            topic_name=topic_name,
            description=description,
            category_id=category_id,
            created_at=created_at,
            has_materials=False
        )
    
    def get_topics_by_category(self, category_id: str) -> List[TopicResponse]:
        results = self.vector_db.get(
            where={
                "$and": [
                    {"category_id": {"$eq": category_id}},
                    {"type": {"$eq": "topic"}}
                ]
            },
            include=["metadatas"]
        )
        
        topics = []
        if results and results["metadatas"]:
            for meta in results["metadatas"]:
                topics.append(TopicResponse(
                    topic_id=meta["topic_id"],
                    topic_name=meta["topic_name"],
                    description=meta.get("description"),
                    category_id=meta.get("category_id"),
                    created_at=datetime.fromisoformat(meta["created_at"]),
                    has_materials=False
                ))
        
        return topics
    
    def get_topics_by_user(self, user_id: str) -> List[TopicResponse]:
        """Get all topics for a user, including those without a category."""
        results = self.vector_db.get(
            where={
                "$and": [
                    {"user_id": {"$eq": user_id}},
                    {"type": {"$eq": "topic"}}
                ]
            },
            include=["metadatas"]
        )
        
        topics = []
        if results and results["metadatas"]:
            for meta in results["metadatas"]:
                topics.append(TopicResponse(
                    topic_id=meta["topic_id"],
                    topic_name=meta["topic_name"],
                    description=meta.get("description"),
                    category_id=meta.get("category_id"),  # May be None
                    created_at=datetime.fromisoformat(meta["created_at"]),
                    has_materials=False
                ))
        
        return topics
    
    def get_topic(self, topic_id: str) -> Optional[TopicResponse]:
        results = self.vector_db.get(
            ids=[topic_id],
            include=["metadatas"]
        )
        
        if results and results["metadatas"]:
            meta = results["metadatas"][0]
            return TopicResponse(
                topic_id=meta["topic_id"],
                topic_name=meta["topic_name"],
                description=meta.get("description"),
                category_id=meta["category_id"],
                created_at=datetime.fromisoformat(meta["created_at"]),
                has_materials=False
            )
        return None
    
    def delete_topic(self, topic_id: str) -> bool:
        try:
            self.vector_db.delete(ids=[topic_id])
            logger.info(f"Deleted topic {topic_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete topic {topic_id}: {e}")
            return False


def get_topic_service() -> TopicService:
    return TopicService.get_instance()
