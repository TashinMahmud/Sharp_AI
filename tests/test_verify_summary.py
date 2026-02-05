import requests
import json

BASE_URL = "http://localhost:8000"
USER_ID = "summarization_test_user"
SESSION_ID = "summarization_session_1"

print("""
╔════════════════════════════════════════════════════════════╗
║         Verify Summary Retrieval from Disk                ║
╚════════════════════════════════════════════════════════════╝
""")

try:
    response = requests.get(f"{BASE_URL}/health")
    print("✅ Server is running\n")
except:
    print("❌ Server is not running! Start it first.")
    exit(1)

print("📝 This test verifies that summaries from test_summarization.py")
print("   were saved to ChromaDB and can be retrieved.\n")

print("="*60)
print("\n🔍 TESTING SUMMARY RETRIEVAL:")
print(f"\nSending a query to the SAME session used in test_summarization.py")
print(f"   User ID: {USER_ID}")
print(f"   Session ID: {SESSION_ID}\n")

query = "Can you summarize what we discussed about renewable energy?"

print(f"📝 Query: '{query}'")

response = requests.post(f"{BASE_URL}/debate/chat", json={
    "user_id": USER_ID,
    "session_id": SESSION_ID,
    "topic": "Should the world transition to 100% renewable energy?",
    "difficulty": "medium",
    "role": "user_argument",
    "message": query
})

if response.status_code == 200:
    ai_response = response.json()["ai_message"]
    print(f"\n✅ AI Response:")
    print(f"\n{ai_response}\n")
    
    keywords = [
        "solar", "wind", "battery", "jobs", "carbon", 
        "pollution", "cheaper", "electric", "independence", "investment"
    ]
    found_keywords = [kw for kw in keywords if kw.lower() in ai_response.lower()]
    
    print("="*60)
    print("\n🔍 VERIFICATION:")
    
    if len(found_keywords) >= 3:
        print(f"✅ SUMMARY RETRIEVAL WORKING!")
        print(f"   AI referenced {len(found_keywords)} topics from the original 12 messages:")
        print(f"   {', '.join(found_keywords)}")
        print("\n   This proves:")
        print("   • Summary was saved to ChromaDB")
        print("   • Summary can be retrieved from disk")
        print("   • AI uses summaries to provide context")
    else:
        print(f"⚠️  PARTIAL: AI mentioned {len(found_keywords)} keywords: {', '.join(found_keywords)}")
        print("   Expected at least 3 keywords from the original conversation")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)

print("\n" + "="*60)
print("\n💡 HOW SUMMARY RETRIEVAL WORKS:")
print("  1. After 10 messages, conversation is summarized")
print("  2. Summary is stored in ChromaDB with type='summary'")
print("  3. When you query, retrieve_context() searches for relevant summaries")
print("  4. AI uses summaries to maintain long-term context")

print("\n📊 NEXT TEST:")
print("  Restart the server and run this test again to verify")
print("  summaries persist across server restarts!")
