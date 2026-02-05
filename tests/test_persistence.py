
import sys
import os
import shutil

sys.path.append(os.getcwd())

from app.services.memory_service import MemoryService
from langchain_core.messages import HumanMessage, AIMessage

def test_persistence():
    user_id = "test_user_persist"
    session_id = "session_persist_1"
    
    print("Initializing MemoryService...")
    service = MemoryService.get_instance()
    
    print("Saving turns to persistence...")
    service.save_turn_persistent(user_id, session_id, "Hello, are you there?", "Yes, I am here.")
    service.save_turn_persistent(user_id, session_id, "What is 2+2?", "2+2 is 4.")
    
    print("Clearing in-memory cache (Simulating Restart)...")
    service._active_sessions.clear()
    
    print("Reloading memory for session...")
    memory = service.get_or_create_memory(user_id, session_id)
    
    history = memory.load_memory_variables({})["chat_history"]
    print(f"Loaded {len(history)} messages.")
    
    for msg in history:
        type_Str = "User" if isinstance(msg, HumanMessage) else "AI"
        print(f"{type_Str}: {msg.content}")
        
    assert len(history) >= 4, "Should have loaded at least 4 messages (2 turns)"
    assert history[0].content == "Hello, are you there?"
    assert history[3].content == "2+2 is 4."
    
    print("\nSUCCESS: Memory reconstructed from disk!")

if __name__ == "__main__":
    test_persistence()
