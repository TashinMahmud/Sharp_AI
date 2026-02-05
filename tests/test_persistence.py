
import sys
import os
import shutil

# Add project root to path
sys.path.append(os.getcwd())

from app.services.memory_service import MemoryService
from langchain_core.messages import HumanMessage, AIMessage

def test_persistence():
    user_id = "test_user_persist"
    session_id = "session_persist_1"
    
    # 1. Initialize Service
    print("Initializing MemoryService...")
    service = MemoryService.get_instance()
    
    # Clear any existing data for this session (for clean test)
    # Note: Chroma doesn't have easy delete by metadata in all versions, 
    # but strictly for this test we'll just use a unique session ID.
    
    # 2. Add data to persistence (Save Turn)
    print("Saving turns to persistence...")
    service.save_turn_persistent(user_id, session_id, "Hello, are you there?", "Yes, I am here.")
    service.save_turn_persistent(user_id, session_id, "What is 2+2?", "2+2 is 4.")
    
    # 3. CLEAER IN-MEMORY CACHE (Simulate Server Restart)
    print("Clearing in-memory cache (Simulating Restart)...")
    service._active_sessions.clear()
    
    # 4. Re-load memory
    print("Reloading memory for session...")
    memory = service.get_or_create_memory(user_id, session_id)
    
    # 5. Verify Content
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
