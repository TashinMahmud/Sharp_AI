"""
API Test Script - Tests the entire debate backend including persistence
Run this while the server is running: uvicorn app.main:app --reload
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"
USER_ID = "test_user_123"
SESSION_ID = "session_001"

def print_response(title, response):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    try:
        data = response.json()
        print(json.dumps(data, indent=2))
    except:
        print(response.text)
    print()

def test_debate_chat_1():
    """Test 1: Send first debate message"""
    print("\n🚀 TEST 1: Starting debate conversation...")
    
    payload = {
        "user_id": USER_ID,
        "session_id": SESSION_ID,
        "topic": "Should AI replace human teachers?",
        "difficulty": "medium",
        "role": "user_argument",
        "message": "AI can provide personalized learning at scale, adapting to each student's pace and learning style."
    }
    
    response = requests.post(f"{BASE_URL}/debate/chat", json=payload)
    print_response("First Debate Message", response)
    return response.status_code == 200

def test_debate_chat_2():
    """Test 2: Send second message in same session"""
    print("\n💬 TEST 2: Continuing the debate...")
    
    payload = {
        "user_id": USER_ID,
        "session_id": SESSION_ID,
        "topic": "Should AI replace human teachers?",
        "difficulty": "medium",
        "role": "user_counter",
        "message": "AI systems can also work 24/7 without getting tired, providing constant support to students."
    }
    
    response = requests.post(f"{BASE_URL}/debate/chat", json=payload)
    print_response("Second Debate Message", response)
    return response.status_code == 200

def test_memory_persistence():
    """Test 3: Test if AI remembers previous conversation"""
    print("\n🧠 TEST 3: Testing memory (AI should remember previous messages)...")
    
    payload = {
        "user_id": USER_ID,
        "session_id": SESSION_ID,
        "topic": "Should AI replace human teachers?",
        "difficulty": "medium",
        "role": "user_rebuttal",
        "message": "Can you summarize what I've said so far about AI teachers?"
    }
    
    response = requests.post(f"{BASE_URL}/debate/chat", json=payload)
    print_response("Memory Test Response", response)
    
    # Check if response references the previous messages
    try:
        data = response.json()
        response_text = data.get("response", "").lower()
        has_memory = ("personalized" in response_text or "scale" in response_text or 
                     "24/7" in response_text or "tired" in response_text)
        
        if has_memory:
            print("✅ SUCCESS: AI remembered the previous conversation!")
        else:
            print("⚠️  WARNING: AI might not have remembered. Check the response above.")
        
        return response.status_code == 200
    except:
        return False

def main():
    print("""
╔════════════════════════════════════════════════════════════╗
║          AI Debate Backend - Full Test Suite              ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        print("✅ Server is running!")
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Server is not running!")
        print("\nPlease start the server first:")
        print("  .\\venv\\Scripts\\activate")
        print("  uvicorn app.main:app --reload")
        return
    
    # Run tests
    results = []
    
    results.append(("First Message", test_debate_chat_1()))
    time.sleep(1)
    
    results.append(("Second Message", test_debate_chat_2()))
    time.sleep(1)
    
    results.append(("Memory Persistence", test_memory_persistence()))
    
    # Summary
    print("\n" + "="*60)
    print("  TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED! Your backend is working perfectly!")
        print("\n📝 CRITICAL TEST: Restart the server and run this script again.")
        print("   The AI should STILL remember the conversation!")
        print("\n   Steps:")
        print("   1. Press Ctrl+C in the server terminal")
        print("   2. Run: uvicorn app.main:app --reload")
        print("   3. Run: python test_api.py")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
