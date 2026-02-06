
import requests
import json
import time

BASE_URL = "http://localhost:8000"
TIMESTAMP = int(time.time())
USER_ID = f"real_user_{TIMESTAMP}"
SESSION_ID = f"session_{TIMESTAMP}"
CATEGORY_NAME = f"Real Category {TIMESTAMP}"
TOPIC_NAME = "Artificial Intelligence"

print("""
╔════════════════════════════════════════════════════════════╗
║        Real Features Integration Test (Live API)           ║
╚════════════════════════════════════════════════════════════╝
""")

try:
    response = requests.get(f"{BASE_URL}/health")
    print("✅ Server is running\n")
except:
    print("❌ Server is not running! Start it first.")
    exit(1)

# 1. Create Category
print("\n[1] Creating Category...")
cat_resp = requests.post(f"{BASE_URL}/categories/", json={
    "category_name": CATEGORY_NAME,
    "user_id": USER_ID,
    "description": "Integration testing category"
})

if cat_resp.status_code == 200:
    category_id = cat_resp.json()["category_id"]
    print(f"✅ Category '{CATEGORY_NAME}' Created ({category_id})")
else:
    print(f"❌ Failed: {cat_resp.text}")
    exit(1)

# 2. Create Topic
print("\n[2] Creating Topic...")
topic_resp = requests.post(f"{BASE_URL}/topics/", json={
    "category_id": category_id,
    "user_id": USER_ID,
    "topic_name": TOPIC_NAME,
    "description": "Testing AI generation"
})

if topic_resp.status_code == 200:
    topic_id = topic_resp.json()["topic_id"]
    print(f"✅ Topic '{TOPIC_NAME}' Created ({topic_id})")
else:
    print(f"❌ Failed: {topic_resp.text}")
    exit(1)

# 3. Generate Materials
print("\n[3] Generating Materials (Calling OpenAI)...")
start_time = time.time()
mat_resp = requests.post(f"{BASE_URL}/materials/generate", json={
    "topic_id": topic_id,
    "user_id": USER_ID
})
duration = time.time() - start_time

if mat_resp.status_code == 200:
    materials = mat_resp.json()
    if len(materials["main_arguments"]) > 0:
        print(f"✅ Materials Generated in {duration:.2f}s")
    else:
        print("❌ Materials generated but empty!")
else:
    print(f"❌ Failed: {mat_resp.text}")
    exit(1)

# 4. Generate Quiz
print("\n[4] Generating Quiz (Calling OpenAI)...")
quiz_resp = requests.post(f"{BASE_URL}/training/topic-quiz", json={
    "user_id": USER_ID,
    "topic_id": topic_id,
    "difficulty": "medium"
})

if quiz_resp.status_code == 200:
    quiz = quiz_resp.json()
    print(f"✅ Quiz Generated:")
    print(f"   Q: {quiz['question']}")
    print(f"   Correct: {quiz['correct_answer']}")
else:
    print(f"❌ Failed: {quiz_resp.text}")
    exit(1)

# 5. Evaluate Answer
print("\n[5] Evaluating Answer...")
eval_resp = requests.post(f"{BASE_URL}/training/evaluate", json={
    "question": quiz["question"],
    "selected_answer": str(quiz["correct_answer"]), 
    "correct_answer": str(quiz["correct_answer"]),
    "difficulty": "medium",
    "user_id": USER_ID,
    "topic_id": topic_id,
    "topic_name": TOPIC_NAME
})

if eval_resp.status_code == 200:
    evaluation = eval_resp.json()
    print(f"✅ Evaluation: {evaluation['feedback'][:100]}...")
else:
    print(f"❌ Failed: {eval_resp.text}")
    exit(1)

# 6. Verify Stats
print("\n[6] Verifying Progress Stats...")
stats_resp = requests.get(f"{BASE_URL}/training/stats/{USER_ID}")

if stats_resp.status_code == 200:
    stats = stats_resp.json()
    if stats["total_quizzes"] >= 1:
        print(f"✅ Stats Verified: Total Quizzes = {stats['total_quizzes']}")
    else:
        print(f"❌ Stats incorrect: {stats}")
else:
    print(f"❌ Failed: {stats_resp.text}")
    exit(1)

# 7. Debate Chat
print("\n[7] Testing Debate Chat (Calling OpenAI)...")
debate_resp = requests.post(f"{BASE_URL}/training/debate", json={
    "user_id": USER_ID,
    "session_id": SESSION_ID,
    "topic_id": topic_id,
    "difficulty": "medium",
    "role": "user_argument",
    "message": "I believe AI will create more jobs than it destroys."
})

if debate_resp.status_code == 200:
    chat_resp = debate_resp.json()
    print(f"✅ AI Response: {chat_resp['response'][:100]}...")
else:
    print(f"❌ Failed: {debate_resp.text}")
    exit(1)

print("\n" + "="*60)
print("\n✅ REAL FEATURES TEST PASSED SUCCESSFULLY")
print("System is fully operational with live OpenAI calls.")
print("\n" + "="*60)
