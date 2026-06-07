import random
import logging
from datetime import datetime

from typing import List, Optional



from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

from app.core.config import get_settings
from app.models.category import Category, CategoryCreate, CategoryResponse

logger = logging.getLogger(__name__)


class CategoryService:
    _instance = None
    
    def __init__(self):
        try:
            self.settings = get_settings()
            if self.settings.openai_api_key:
                self.embeddings = OpenAIEmbeddings(
                    api_key=self.settings.openai_api_key,
                    model="text-embedding-3-small"
                )
            else:
                from langchain_core.embeddings import FakeEmbeddings
                self.embeddings = FakeEmbeddings(size=1536)
            
            logger.info(f"Initializing CategoryService with ChromaDB at {self.settings.chroma_path}")
            self.vector_db = Chroma(
                persist_directory=self.settings.chroma_path,
                embedding_function=self.embeddings,
                collection_name="user_categories"
            )
        except Exception as e:
            logger.error(f"Failed to initialize CategoryService: {e}")
            raise
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def create_category(self, user_id: int, category_name: str) -> CategoryResponse:
        category_id = random.randint(1, 2147483647)
        created_at = datetime.now()
        
        metadata = {
            "category_id": category_id,
            "user_id": user_id,
            "category_name": category_name,
            "created_at": created_at.isoformat(),
            "type": "category"
        }
        
        self.vector_db.add_texts(
            texts=[f"Category: {category_name}"],
            metadatas=[metadata],
            ids=[str(category_id)]
        )
        
        logger.info(f"Created category {category_id} for user {user_id}")
        
        return CategoryResponse(
            category_id=category_id,
            category_name=category_name,
            created_at=created_at,
            topic_count=0
        )
    
    def get_categories(self, user_id: int) -> List[CategoryResponse]:
        results = self.vector_db.get(
            where={
                "$and": [
                    {"user_id": {"$eq": user_id}},
                    {"type": {"$eq": "category"}}
                ]
            },
            include=["metadatas"]
        )
        
        categories = []
        if results and results["metadatas"]:
            for meta in results["metadatas"]:
                categories.append(CategoryResponse(
                    category_id=meta["category_id"],
                    category_name=meta["category_name"],
                    created_at=datetime.fromisoformat(meta["created_at"]),
                    topic_count=0
                ))
        
        return categories
    
    def delete_category(self, category_id: int) -> bool:
        try:
            self.vector_db.delete(ids=[str(category_id)])
            logger.info(f"Deleted category {category_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete category {category_id}: {e}")
            return False


def get_category_service() -> CategoryService:
    return CategoryService.get_instance()
