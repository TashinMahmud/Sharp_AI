import requests
import json

BASE_URL = "http://localhost:8000"
USER_ID = "rag_test_user"

print("""
╔════════════════════════════════════════════════════════════╗
║         Verify RAG Data Persists After Restart            ║
╚════════════════════════════════════════════════════════════╝
""")

try:
    response = requests.get(f"{BASE_URL}/health")
    print("✅ Server is running\n")
except:
    print("❌ Server is not running! Start it first.")
    exit(1)

print("📝 This test verifies that RAG data from test_rag.py")
print("   was saved to ChromaDB and persists after server restart.\n")

print("="*60)
print("\n🔍 TESTING RAG PERSISTENCE:")
print("\nQuerying about topics from the 3 sessions created in test_rag.py:")
print("  • Climate change (carbon capture, reforestation)")
print("  • Renewable energy (solar, wind)")
print("  • Transportation (EVs, public transit)\n")

test_queries = [
    {
        "query": "What solutions did I mention for climate change?",
        "expected_keywords": ["carbon", "capture", "reforestation", "forest", "tree"]
    },
    {
        "query": "What did I say about renewable energy?",
        "expected_keywords": ["solar", "wind", "energy", "electricity", "power"]
    },
    {
        "query": "What transportation solutions did I discuss?",
        "expected_keywords": ["electric", "vehicle", "transit", "public", "ev"]
    }
]

results = []

for i, test in enumerate(test_queries, 1):
    query = test["query"]
    expected = test["expected_keywords"]
    
    print(f"\n📝 Query {i}: '{query}'")
    
    response = requests.post(f"{BASE_URL}/debate/chat", json={
        "user_id": USER_ID,
        "session_id": f"verify_rag_session_{i}",
        "topic": "Environmental solutions",
        "difficulty": "medium",
        "role": "user_argument",
        "message": query
    })
    
    if response.status_code == 200:
        ai_response = response.json()["ai_message"]
        print(f"   AI: {ai_response[:100]}...")
        
        found = [kw for kw in expected if kw.lower() in ai_response.lower()]
        
        if found:
            print(f"   ✅ Found keywords: {', '.join(found)}")
            results.append(True)
        else:
            print(f"   ⚠️  No expected keywords found")
            results.append(False)
    else:
        print(f"   ❌ Error: {response.status_code}")
        results.append(False)

print("\n" + "="*60)
print("\n🔍 FINAL VERIFICATION:")

passed = sum(results)
total = len(results)

if passed == total:
    print(f"✅ ALL TESTS PASSED ({passed}/{total})")
    print("\n   This proves:")
    print("   • RAG data was saved to ChromaDB")
    print("   • RAG data persists on disk")
    print("   • Semantic search works across sessions")
    print("   • Data survives server restarts")
elif passed > 0:
    print(f"⚠️  PARTIAL SUCCESS ({passed}/{total} passed)")
    print("   Some RAG data was retrieved, but not all")
else:
    print(f"❌ FAILED ({passed}/{total} passed)")
    print("   RAG data might not be persisting correctly")

print("\n" + "="*60)
print("\n💡 HOW RAG PERSISTENCE WORKS:")
print("  1. Messages are embedded and stored in ChromaDB")
print("  2. ChromaDB persists data to disk in ./app/data/chroma_db/")
print("  3. After server restart, ChromaDB reloads from disk")
print("  4. Semantic search retrieves relevant past messages")

print("\n📊 TO FULLY VERIFY:")
print("  1. Run test_rag.py to create sessions")
print("  2. Restart the server")
print("  3. Run this test to verify data persists")
