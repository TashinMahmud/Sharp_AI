import requests
import json
import time

BASE_URL = "http://localhost:8000"
USER_ID = "summarization_test_user"
SESSION_ID = "summarization_session_1"

print("""
╔════════════════════════════════════════════════════════════╗
║        Summarization & Memory Pruning Test                ║
╚════════════════════════════════════════════════════════════╝
""")

try:
    response = requests.get(f"{BASE_URL}/health")
    print("✅ Server is running\n")
except:
    print("❌ Server is not running! Start it first.")
    exit(1)

print("📝 Sending 12 messages to trigger summarization...")
print("   (Default trigger: 10 messages, configured in .env)\n")

messages = [
    ("user_argument", "Renewable energy is essential for combating climate change."),
    ("user_counter", "Solar and wind power are now cheaper than fossil fuels in many regions."),
    ("user_rebuttal", "Renewable energy creates more jobs than traditional energy sectors."),
    ("user_argument", "Battery technology is improving rapidly, solving storage issues."),
    ("user_counter", "Countries with high renewable adoption have lower carbon emissions."),
    ("user_rebuttal", "Renewable energy reduces air pollution and health costs."),
    ("user_argument", "Solar panels have become 90% cheaper in the last decade."),
    ("user_counter", "Wind energy capacity has doubled globally in 5 years."),
    ("user_rebuttal", "Renewable energy enhances energy independence and security."),
    ("user_argument", "Electric vehicles powered by renewables eliminate transport emissions."),
    ("user_counter", "Renewable energy infrastructure creates resilient power grids."),
    ("user_rebuttal", "Green energy investments yield better long-term returns."),
]

for i, (role, message) in enumerate(messages, 1):
    print(f"Message {i}/12: {message[:50]}...")
    
    response = requests.post(f"{BASE_URL}/debate/chat", json={
        "user_id": USER_ID,
        "session_id": SESSION_ID,
        "topic": "Should the world transition to 100% renewable energy?",
        "difficulty": "medium",
        "role": role,
        "message": message
    })
    
    if response.status_code == 200:
        print(f"  ✅ Sent (AI responded)")
    else:
        print(f"  ❌ Error: {response.status_code}")
        print(f"  {response.text}")
        break
    
    time.sleep(0.5)

print("\n" + "="*60)
print("\n🔍 VERIFICATION:")
print("\nIf summarization triggered (after message 10):")
print("  ✅ Server logs should show: 'Summarizing conversation'")
print("  ✅ Older messages should be pruned from RAM")
print("  ✅ Summary should be stored in ChromaDB")
print("\nCheck your server terminal for log messages!")

print("\n" + "="*60)
print("\n📊 To verify summarization worked:")
print("  1. Check server logs for 'Summarizing conversation'")
print("  2. Send one more message and see if AI still has context")
print("  3. Restart server and verify memory reconstruction")

print("\n💡 TIP: Check .env file - MEMORY_SUMMARY_TRIGGER=10")
print("         Adjust this value to test different thresholds")
