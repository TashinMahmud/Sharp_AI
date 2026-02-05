
import os
import shutil
import logging
from typing import Optional, Dict, Tuple, List
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.memory import ConversationBufferMemory
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
            
            # 1. Initialize Embeddings
            self.embeddings = OpenAIEmbeddings(
                api_key=self.settings.openai_api_key,
                model="text-embedding-3-small"
            )
            
            # 2. Initialize ChromaDB (Persistent)
            logger.info(f"Initializing ChromaDB at {self.settings.chroma_path}")
            self.vector_db = Chroma(
                persist_directory=self.settings.chroma_path,
                embedding_function=self.embeddings,
                collection_name="debate_history"
            )
            
            # 3. Initialize Short-term Memory Store (In-Memory)
            # Key: (user_id, session_id) -> Value: ConversationBufferMemory
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
        """Get active session memory or create new one, rebuilding from disk if needed."""
        key = (user_id, session_id)
        if key not in self._active_sessions:
            # Create new memory
            memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                output_key="ai_message",
                input_key="user_message"
            )
            
            # Try to load existing history from Chroma
            try:
                logger.info(f"Attempting to rebuild session {session_id} for user {user_id} from disk")
                self._rebuild_memory_from_disk(user_id, session_id, memory)
            except Exception as e:
                logger.error(f"Failed to rebuild memory from disk: {e}")
            
            self._active_sessions[key] = memory
            
        return self._active_sessions[key]

    def _rebuild_memory_from_disk(self, user_id: str, session_id: str, memory: ConversationBufferMemory):
        """Re-populate a fresh ConversationBufferMemory with turns from ChromaDB."""
        # Retrieve recent turns
        turns = self.vector_db.similarity_search(
            query=" ", # Dummy query to match filter
            k=20, # Load last 20 turns
            filter={
                "$and": [
                    {"user_id": {"$eq": user_id}},
                    {"session_id": {"$eq": session_id}},
                    {"type": {"$eq": "turn"}},
                ]
            }
        )
        
        # Sort by timestamp (if we had one, but Chroma doesn't strictly order by metadata without custom logic)
        # Since similarity_search might not respect chronological order perfectly without custom retrieval,
        # we'll assume for now standard retrieval. proper implementation would require ordering.
        # However, for this implementation lets rely on standard retrieval or we'd need to fetch all and sort python side.
        
        # NOTE: A better approach for exact history is storing a separate timestamp and sorting.
        # But `similarity_search` returns by relevance. 
        # Chroma doesn't easily support "get last N by date". 
        # Workaround: We will rely on the fact that we might just get "relevant" context if using similarity search.
        # BUT the requirement is "Rebuild session".
        # So we should actually just fetch *all* for this session? Or relying on "relevant" is tricky for linear history.
        # Let's adjust: We can try to fetch by filter.
        
        # Actually, for true session reconstruction, a vector DB is slightly mismatched if used purely for linear history retrieval without vector search.
        # But we can use `get` instead of `similarity_search` if we know IDs, or just filter.
        # Chroma `get` supports filtering.
        
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
        
        # Manual sorting by timestamp
        if results and results["documents"]:
            combined = []
            for i, doc in enumerate(results["documents"]):
                meta = results["metadatas"][i]
                combined.append({"content": doc, "metadata": meta})
            
            # Sort by timestamp
            combined.sort(key=lambda x: x["metadata"].get("timestamp", 0))
            
            # Replay into memory
            for item in combined:
                role = item["metadata"].get("role")
                content = item["content"]
                
                # Ensure content is a string
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
        """Save a turn to ChromaDB immediately."""
        import time
        timestamp = time.time()
        
        # Ensure messages are strings
        if not isinstance(user_msg, str):
            logger.warning(f"user_msg is not a string: {type(user_msg)}, converting...")
            user_msg = str(user_msg)
        
        if not isinstance(ai_msg, str):
            logger.warning(f"ai_msg is not a string: {type(ai_msg)}, converting...")
            ai_msg = str(ai_msg)
        
        # Save User Message
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
        
        # Save AI Message (slightly later timestamp to ensure order)
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
        """Save a single turn to short-term memory (RAM)."""
        memory = self.get_or_create_memory(user_id, session_id)
        memory.save_context(
            {"user_message": user_msg}, 
            {"ai_message": ai_msg}
        )

    def summarize_and_store(self, user_id: str, session_id: str, summary: str):
        """Store a conversation summary into long-term vector DB."""
        # Ensure summary is a string
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
        """Retrieve relevant past context from ChromaDB."""
        # Filter by user_id to ensure privacy
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
        """Clear short-term memory for a session."""
        key = (user_id, session_id)
        if key in self._active_sessions:
            self._active_sessions[key].clear()
