import requests
import json

BASE_URL = "http://localhost:8000"

print("""
╔════════════════════════════════════════════════════════════╗
║   Manual Test - Part 2: Testing Persistent Memory         ║
╚════════════════════════════════════════════════════════════╝
""")

print("🔄 Server has been restarted. Testing if memory persists...\n")

try:
    health = requests.get(f"{BASE_URL}/health")
    print("✅ Server is running\n")
except:
    print("❌ Server is not running! Start it first.")
    exit(1)

print("="*60 + "\n")

print("🧠 Asking AI to recall the conversation from BEFORE restart...")
response = requests.post(f"{BASE_URL}/debate/chat", json={
    "user_id": "manual_test_user",
    "session_id": "manual_session_1",
    "topic": "Should humanity prioritize Mars colonization?",
    "difficulty": "medium",
    "role": "user_rebuttal",
    "message": "Remind me what I said earlier about Mars colonization."
})

print(f"Status: {response.status_code}")

if response.status_code == 200:
    ai_message = response.json()['ai_message']
    print("\n📋 AI's Response:")
    print(f"\n{ai_message}\n")
    
    remembered_survival = "survival" in ai_message.lower() or "uninhabitable" in ai_message.lower() or "earth" in ai_message.lower()
    remembered_innovation = "innovation" in ai_message.lower() or "technological" in ai_message.lower() or "scientific" in ai_message.lower() or "discoveries" in ai_message.lower()
    
    print("="*60)
    print("\n🔍 VERIFICATION:")
    
    if remembered_survival:
        print("✅ AI remembered: Humanity's survival / Earth uninhabitable")
    else:
        print("❌ AI forgot: Survival argument")
    
    if remembered_innovation:
        print("✅ AI remembered: Technological innovation / scientific discoveries")
    else:
        print("❌ AI forgot: Innovation argument")
    
    print("\n" + "="*60)
    
    if remembered_survival and remembered_innovation:
        print("\n🎉 SUCCESS! PERSISTENT MEMORY IS WORKING!")
        print("   The AI remembered the conversation from BEFORE the restart!")
    elif remembered_survival or remembered_innovation:
        print("\n⚠️  PARTIAL SUCCESS: AI remembered some but not all points")
    else:
        print("\n❌ FAILED: AI did not remember the previous conversation")
else:
    print(f"❌ Error: {response.text}")

print("\n" + "="*60)
