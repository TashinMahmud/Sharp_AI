import random
import logging
from datetime import datetime

from typing import List, Optional



from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

from app.core.config import get_settings
from app.models.material import TrainingMaterial, MaterialGenerate, MaterialResponse
from app.services.ai_service import AIService

logger = logging.getLogger(__name__)


class MaterialService:
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
            
            logger.info(f"Initializing MaterialService with ChromaDB at {self.settings.chroma_path}")
            self.vector_db = Chroma(
                persist_directory=self.settings.chroma_path,
                embedding_function=self.embeddings,
                collection_name="topic_materials"
            )
            
            self.ai_service = AIService.get_instance()
        except Exception as e:
            logger.error(f"Failed to initialize MaterialService: {e}")
            raise
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def generate_and_save_materials(
        self, 
        user_id: int, 
        topic_id: int, 
        topic_name: str, 
        description: Optional[str] = None,
        difficulty: int = 3
    ) -> MaterialResponse:
        
        logger.info(f"Generating materials for topic {topic_id}: {topic_name}")
        
        generated = self.ai_service.generate_arguments(
            topic=topic_name if not description else f"{topic_name}: {description}",
            difficulty=difficulty
        )
        
        material_id = random.randint(1, 2147483647)
        created_at = datetime.now()
        
        metadata = {
            "material_id": material_id,
            "user_id": user_id,
            "topic_id": topic_id,
            "topic_name": topic_name,
            "difficulty": difficulty,
            "created_at": created_at.isoformat(),
            "type": "material",
            "main_arguments": str(generated["content"]["main_arguments"]),
            "counter_arguments": str(generated["content"]["counter_arguments"]),
            "rebuttals": str(generated["content"]["rebuttals"])
        }
        
        text_content = f"Topic: {topic_name}\n"
        text_content += f"Arguments: {', '.join(generated['content']['main_arguments'])}\n"
        text_content += f"Counters: {', '.join(generated['content']['counter_arguments'])}\n"
        text_content += f"Rebuttals: {', '.join(generated['content']['rebuttals'])}"
        
        self.vector_db.add_texts(
            texts=[text_content],
            metadatas=[metadata],
            ids=[str(material_id)]
        )
        
        logger.info(f"Saved materials {material_id} for topic {topic_id}")
        
        return MaterialResponse(
            material_id=material_id,
            topic_id=topic_id,
            main_arguments=generated["content"]["main_arguments"],
            counter_arguments=generated["content"]["counter_arguments"],
            rebuttals=generated["content"]["rebuttals"],
            difficulty=difficulty,
            created_at=created_at
        )
    
    def get_materials_by_topic(self, topic_id: int) -> Optional[MaterialResponse]:
        results = self.vector_db.get(
            where={
                "$and": [
                    {"topic_id": {"$eq": topic_id}},
                    {"type": {"$eq": "material"}}
                ]
            },
            include=["metadatas"]
        )
        
        if results and results["metadatas"]:
            meta = results["metadatas"][0]
            return MaterialResponse(
                material_id=meta["material_id"],
                topic_id=meta["topic_id"],
                main_arguments=eval(meta["main_arguments"]),
                counter_arguments=eval(meta["counter_arguments"]),
                rebuttals=eval(meta["rebuttals"]),
                difficulty=meta["difficulty"],
                created_at=datetime.fromisoformat(meta["created_at"])
            )
        return None
    
    def delete_materials(self, topic_id: int) -> bool:
        try:
            results = self.vector_db.get(
                where={
                    "$and": [
                        {"topic_id": {"$eq": topic_id}},
                        {"type": {"$eq": "material"}}
                    ]
                }
            )
            
            if results and results["ids"]:
                self.vector_db.delete(ids=results["ids"])
                logger.info(f"Deleted materials for topic {topic_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete materials for topic {topic_id}: {e}")
            return False


def get_material_service() -> MaterialService:
    return MaterialService.get_instance()
