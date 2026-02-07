
import os
import shutil
import logging
from typing import Optional, Dict, Tuple, List




from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

from app.core.config import get_settings

logger = logging.getLogger(__name__)

class MemoryService:
    _instance = None
    
    def __init__(self):
        try:
            self.settings = get_settings()
            
            self.embeddings = OpenAIEmbeddings(
                api_key=self.settings.openai_api_key,
                model="text-embedding-3-small"
            )
            
            logger.info(f"Initializing ChromaDB at {self.settings.chroma_path}")
            self.vector_db = Chroma(
                persist_directory=self.settings.chroma_path,
                embedding_function=self.embeddings,
                collection_name="debate_history"
            )
            
            self._active_sessions: Dict[Tuple[str, str], ConversationBufferMemory] = {}
        except Exception as e:
            logger.error(f"Failed to initialize MemoryService: {e}")
            raise

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


    def get_or_create_memory(self, user_id: str, session_id: str) -> ConversationBufferMemory:
        key = (user_id, session_id)
        if key not in self._active_sessions:
            memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                output_key="ai_message",
                input_key="user_message"
            )
            
            try:
                logger.info(f"Attempting to rebuild session {session_id} for user {user_id} from disk")
                self._rebuild_memory_from_disk(user_id, session_id, memory)
            except Exception as e:
                logger.error(f"Failed to rebuild memory from disk: {e}")
            
            self._active_sessions[key] = memory
            
        return self._active_sessions[key]


    def _rebuild_memory_from_disk(self, user_id: str, session_id: str, memory: ConversationBufferMemory):
        results = self.vector_db.get(
            where={
                "$and": [
                    {"user_id": {"$eq": user_id}},
                    {"session_id": {"$eq": session_id}},
                    {"type": {"$eq": "turn"}},
                ]
            },
            include=["documents", "metadatas"]
        )
        
        if results and results["documents"]:
            combined = []
            for i, doc in enumerate(results["documents"]):
                meta = results["metadatas"][i]
                combined.append({"content": doc, "metadata": meta})
            
            combined.sort(key=lambda x: x["metadata"].get("timestamp", 0))
            
            for item in combined:
                role = item["metadata"].get("role")
                content = item["content"]
                
                if not isinstance(content, str):
                    logger.warning(f"Content is not a string: {type(content)}, converting...")
                    content = str(content)
                
                try:
                    if role == "user":
                        memory.chat_memory.add_user_message(content)
                    elif role == "ai":
                        memory.chat_memory.add_ai_message(content)
                except Exception as e:
                    logger.error(f"Failed to add message to memory: {e}, content type: {type(content)}")
                    raise

    def save_turn_persistent(self, user_id: str, session_id: str, user_msg: str, ai_msg: str):
        import time
        timestamp = time.time()
        
        if not isinstance(user_msg, str):
            logger.warning(f"user_msg is not a string: {type(user_msg)}, converting...")
            user_msg = str(user_msg)
        
        if not isinstance(ai_msg, str):
            logger.warning(f"ai_msg is not a string: {type(ai_msg)}, converting...")
            ai_msg = str(ai_msg)
        
        doc_user = Document(
            page_content=user_msg,
            metadata={
                "user_id": user_id,
                "session_id": session_id,
                "role": "user",
                "type": "turn",
                "timestamp": timestamp
            }
        )
        
        doc_ai = Document(
            page_content=ai_msg,
            metadata={
                "user_id": user_id,
                "session_id": session_id,
                "role": "ai",
                "type": "turn",
                "timestamp": timestamp + 0.001
            }
        )
        
        self.vector_db.add_documents([doc_user, doc_ai])

    def save_turn(self, user_id: str, session_id: str, user_msg: str, ai_msg: str):
        memory = self.get_or_create_memory(user_id, session_id)
        memory.save_context(
            {"user_message": user_msg}, 
            {"ai_message": ai_msg}
        )

    def summarize_and_store(self, user_id: str, session_id: str, summary: str):
        if not isinstance(summary, str):
            logger.warning(f"Summary is not a string: {type(summary)}, converting...")
            summary = str(summary)
        
        doc = Document(
            page_content=summary,
            metadata={
                "user_id": user_id,
                "session_id": session_id,
                "type": "summary"
            }
        )
        self.vector_db.add_documents([doc])
        logger.info(f"Summary stored for user {user_id}, session {session_id}") 

    def retrieve_context(self, user_id: str, session_id: str, query: str, k: int = 3) -> str:
        results = self.vector_db.similarity_search(
            query,
            k=k,
            filter={"user_id": user_id} 
        )
        
        if not results:
            return ""
            
        context_str = "\n".join([f"- {doc.page_content}" for doc in results])
        return f"Relevant past context:\n{context_str}"

    def clear_session(self, user_id: str, session_id: str):
        key = (user_id, session_id)
        if key in self._active_sessions:
            self._active_sessions[key].clear()
