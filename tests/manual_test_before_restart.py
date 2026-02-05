"""
Manual Test - Step 1: Initial Conversation
Run this BEFORE restarting the server
"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("""
╔════════════════════════════════════════════════════════════╗
║     Manual Test - Part 1: Building Conversation           ║
╚════════════════════════════════════════════════════════════╝
""")

# Test 1: Send first message
print("📝 Sending Message 1: Mars colonization...")
response = requests.post(f"{BASE_URL}/debate/chat", json={
    "user_id": "manual_test_user",
    "session_id": "manual_session_1",
    "topic": "Should humanity prioritize Mars colonization?",
    "difficulty": "medium",
    "role": "user_argument",
    "message": "Mars colonization will ensure humanity's survival if Earth becomes uninhabitable."
})

print(f"Status: {response.status_code}")
if response.status_code == 200:
    print("✅ Message 1 sent successfully")
    print(f"AI Response: {response.json()['ai_message'][:100]}...")
else:
    print(f"❌ Error: {response.text}")

print("\n" + "="*60 + "\n")

# Test 2: Send second message
print("📝 Sending Message 2: Scientific advancement...")
response = requests.post(f"{BASE_URL}/debate/chat", json={
    "user_id": "manual_test_user",
    "session_id": "manual_session_1",
    "topic": "Should humanity prioritize Mars colonization?",
    "difficulty": "medium",
    "role": "user_counter",
    "message": "Mars missions will drive technological innovation and scientific discoveries."
})

print(f"Status: {response.status_code}")
if response.status_code == 200:
    print("✅ Message 2 sent successfully")
    print(f"AI Response: {response.json()['ai_message'][:100]}...")
else:
    print(f"❌ Error: {response.text}")

print("\n" + "="*60 + "\n")

# Test 3: Ask AI to recall
print("🧠 Testing Memory: Asking AI to recall what you said...")
response = requests.post(f"{BASE_URL}/debate/chat", json={
    "user_id": "manual_test_user",
    "session_id": "manual_session_1",
    "topic": "Should humanity prioritize Mars colonization?",
    "difficulty": "medium",
    "role": "user_rebuttal",
    "message": "What were the two main points I made about Mars colonization?"
})

print(f"Status: {response.status_code}")
if response.status_code == 200:
    ai_message = response.json()['ai_message']
    print("✅ Memory test response:")
    print(f"\n{ai_message}\n")
    
    # Check if AI remembered
    if ("survival" in ai_message.lower() or "uninhabitable" in ai_message.lower()) and ("innovation" in ai_message.lower() or "technological" in ai_message.lower() or "scientific" in ai_message.lower()):
        print("✅ SUCCESS: AI remembered BOTH points!")
    else:
        print("⚠️  WARNING: AI might not have remembered both points")
else:
    print(f"❌ Error: {response.text}")

print("\n" + "="*60)
print("\n🔥 NOW RESTART THE SERVER:")
print("   1. Press Ctrl+C in the server terminal")
print("   2. Run: uvicorn app.main:app --reload")
print("   3. Run: python manual_test_after_restart.py")
print("\n" + "="*60)
