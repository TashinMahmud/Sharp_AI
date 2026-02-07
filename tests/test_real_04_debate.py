
import requests
import json
import time

BASE_URL = "http://localhost:8000"
TIMESTAMP = int(time.time())
USER_ID = f"test_user_chat_{TIMESTAMP}"
SESSION_ID = f"sess_{TIMESTAMP}"
TOPIC_NAME = "Remote Work"

def print_header(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_result(step, success, message):
    icon = "✅" if success else "❌"
    print(f"[{step}] {icon} {message}")
    if not success:
        exit(1)

print_header("TEST 04: DEBATE CHAT (Context & Roles)")

# SETUP: Need a topic and materials for context to work best
print("\n--- Setup ---")
c_resp = requests.post(f"{BASE_URL}/categories/", json={"category_name": "Work", "user_id": USER_ID})
cat_id = c_resp.json()["category_id"]
t_resp = requests.post(f"{BASE_URL}/topics/", json={"category_id": cat_id, "user_id": USER_ID, "topic_name": TOPIC_NAME})
topic_id = t_resp.json()["topic_id"]
requests.post(f"{BASE_URL}/materials/generate", json={"topic_id": topic_id, "user_id": USER_ID})

# --- SCENARIO 1: User Argument (Start Debate) ---
print("\n--- Scenario 1: User Arguments (Role: user_argument) ---")
msg1 = "Remote work increases productivity because there are fewer office distractions."
resp1 = requests.post(f"{BASE_URL}/training/debate", json={
    "user_id": USER_ID,
    "session_id": SESSION_ID,
    "topic_id": topic_id,
    "difficulty": "medium",
    "role": "user_argument",
    "message": msg1
})

if resp1.status_code == 200:
    reply = resp1.json()["ai_message"]
    print(f"   AI: {reply[:100]}...")
    print_result(1, True, "AI responded to argument")
else:
    print_result(1, False, f"Failed: {resp1.text}")

# --- SCENARIO 2: User Counter-Argument ---
print("\n--- Scenario 2: User Counter (Role: user_counter) ---")
# Simulate user countering the AI's previous point (conceptually)
msg2 = "However, remote work can lead to isolation and lack of team cohesion."
resp2 = requests.post(f"{BASE_URL}/training/debate", json={
    "user_id": USER_ID,
    "session_id": SESSION_ID,
    "topic_id": topic_id,
    "difficulty": "medium",
    "role": "user_counter",
    "message": msg2
})

if resp2.status_code == 200:
    reply = resp2.json()["ai_message"]
    print(f"   AI: {reply[:100]}...")
    print_result(2, True, "AI responded to counter-argument")
else:
    print_result(2, False, f"Failed: {resp2.text}")

# --- SCENARIO 3: Short/Empty Message (Validation) ---
# Assuming AI handles it gracefully or returns error? Let's assume it should respond asking for elaboration.
print("\n--- Scenario 3: Short Message ---")
msg3 = "No."
resp3 = requests.post(f"{BASE_URL}/training/debate", json={
    "user_id": USER_ID,
    "session_id": SESSION_ID,
    "topic_id": topic_id,
    "difficulty": "hard",
    "role": "user_rebuttal",
    "message": msg3
})

if resp3.status_code == 200:
    reply = resp3.json()["ai_message"]
    print(f"   AI: {reply[:100]}...")
    print_result(3, True, "AI handled short message")
else:
    print_result(3, False, f"Error (Unexpected): {resp3.text}")

print("\n" + "="*60)
print("✅ TEST 04 COMPLETE")
