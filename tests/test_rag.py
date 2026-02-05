import requests
import json
import time

BASE_URL = "http://localhost:8000"
USER_ID = "rag_test_user"

print("""
╔════════════════════════════════════════════════════════════╗
║          RAG (Semantic Retrieval) Test                    ║
╚════════════════════════════════════════════════════════════╝
""")

try:
    response = requests.get(f"{BASE_URL}/health")
    print("✅ Server is running\n")
except:
    print("❌ Server is not running! Start it first.")
    exit(1)

print("📝 Creating multiple sessions with different topics...\n")

print("Session 1: Climate Change Discussion")
sessions = [
    {
        "session_id": "rag_session_climate",
        "topic": "Climate change solutions",
        "messages": [
            ("user_argument", "Carbon capture technology can remove CO2 from the atmosphere."),
            ("user_counter", "Reforestation is a natural and cost-effective carbon solution."),
        ]
    },
    {
        "session_id": "rag_session_energy",
        "topic": "Renewable energy adoption",
        "messages": [
            ("user_argument", "Solar energy is becoming the cheapest form of electricity."),
            ("user_counter", "Wind farms can power entire cities with clean energy."),
        ]
    },
    {
        "session_id": "rag_session_transport",
        "topic": "Sustainable transportation",
        "messages": [
            ("user_argument", "Electric vehicles eliminate tailpipe emissions completely."),
            ("user_counter", "Public transit reduces traffic congestion and pollution."),
        ]
    }
]

for session_data in sessions:
    session_id = session_data["session_id"]
    topic = session_data["topic"]
    
    print(f"\n📂 Session: {session_id}")
    print(f"   Topic: {topic}")
    
    for role, message in session_data["messages"]:
        response = requests.post(f"{BASE_URL}/debate/chat", json={
            "user_id": USER_ID,
            "session_id": session_id,
            "topic": topic,
            "difficulty": "medium",
            "role": role,
            "message": message
        })
        
        if response.status_code == 200:
            print(f"  ✅ Saved: {message[:40]}...")
        else:
            print(f"  ❌ Error: {response.status_code}")
    
    time.sleep(0.5)

print("\n" + "="*60)
print("\n🔍 TESTING RAG RETRIEVAL:")
print("\nSending a query that should retrieve context from previous sessions...")

test_session = "rag_test_new_session"
query = "What did I say about renewable energy solutions?"

print(f"\n📝 Query: '{query}'")
print(f"   Session: {test_session} (NEW)")

response = requests.post(f"{BASE_URL}/debate/chat", json={
    "user_id": USER_ID,
    "session_id": test_session,
    "topic": "Environmental solutions",
    "difficulty": "medium",
    "role": "user_argument",
    "message": query
})

if response.status_code == 200:
    ai_response = response.json()["ai_message"]
    print(f"\n✅ AI Response:")
    print(f"\n{ai_response}\n")
    
    keywords = ["solar", "wind", "electric", "carbon", "reforestation"]
    found_keywords = [kw for kw in keywords if kw.lower() in ai_response.lower()]
    
    print("="*60)
    print("\n🔍 VERIFICATION:")
    
    if found_keywords:
        print(f"✅ RAG WORKING! AI referenced: {', '.join(found_keywords)}")
        print("   The AI retrieved context from previous sessions!")
    else:
        print("⚠️  RAG might not be working - no keywords from previous sessions found")
        print("   Expected keywords: solar, wind, electric, carbon, reforestation")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)

print("\n" + "="*60)
print("\n💡 HOW RAG WORKS:")
print("  1. Your messages are embedded and stored in ChromaDB")
print("  2. When you ask a question, it searches for similar past messages")
print("  3. Relevant context is added to the AI's prompt")
print("  4. The AI can reference information from ANY past session")
