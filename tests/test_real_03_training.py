
import requests
import json
import time

BASE_URL = "http://localhost:8000"
TIMESTAMP = int(time.time())
USER_ID = f"test_user_quiz_{TIMESTAMP}"
CATEGORY_NAME = f"Quiz Test Cat {TIMESTAMP}"
TOPIC_NAME = "Python Programming"

def print_header(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_result(step, success, message):
    icon = "✅" if success else "❌"
    print(f"[{step}] {icon} {message}")
    if not success:
        exit(1)

print_header("TEST 03: TRAINING & QUIZZES")

# PRE-REQUISITE
print("\n--- Setup: Creating Data & Materials ---")
c_resp = requests.post(f"{BASE_URL}/categories/", json={"category_name": CATEGORY_NAME, "user_id": USER_ID})
cat_id = c_resp.json()["category_id"]
t_resp = requests.post(f"{BASE_URL}/topics/", json={"category_id": cat_id, "user_id": USER_ID, "topic_name": TOPIC_NAME})
topic_id = t_resp.json()["topic_id"]
requests.post(f"{BASE_URL}/materials/generate", json={"topic_id": topic_id, "user_id": USER_ID})
print("Setup Complete.")

# --- SCENARIO 1a: Random Quiz (from all user topics) ---
print("\n--- Scenario 1a: Random Quiz ---")
random_quiz_resp = requests.post(f"{BASE_URL}/training/random-quiz", json={
    "user_id": USER_ID,
    "difficulty": "medium"
})
if random_quiz_resp.status_code == 200:
    rq = random_quiz_resp.json()
    print(f"   Q: {rq['question'][:60]}...")
    print_result("1a", True, "Random quiz generated")
else:
    print_result("1a", False, f"Failed: {random_quiz_resp.text}")

# --- SCENARIO 1b: Category Quiz ---
print("\n--- Scenario 1b: Category Quiz ---")
cat_quiz_resp = requests.post(f"{BASE_URL}/training/category-quiz", json={
    "user_id": USER_ID,
    "category_id": cat_id,
    "difficulty": "medium"
})
if cat_quiz_resp.status_code == 200:
    cq = cat_quiz_resp.json()
    print(f"   Q: {cq['question'][:60]}...")
    print_result("1b", True, "Category quiz generated")
else:
    print_result("1b", False, f"Failed: {cat_quiz_resp.text}")

# --- SCENARIO 1c: Topic Quiz (Specific) ---
print("\n--- Scenario 1c: Topic Quiz ---")
quiz_resp = requests.post(f"{BASE_URL}/training/topic-quiz", json={
    "user_id": USER_ID,
    "topic_id": topic_id,
    "difficulty": "medium"
})
if quiz_resp.status_code == 200:
    quiz = quiz_resp.json()
    print(f"   Q: {quiz['question']}")
    print_result("1c", True, "Topic quiz generated")
else:
    print_result("1c", False, f"Failed: {quiz_resp.text}")

# --- SCENARIO 2: Evaluate Correct Answer ---
print("\n--- Scenario 2: Evaluate Correct Answer ---")
correct_val = str(quiz["correct_answer"])
eval_resp = requests.post(f"{BASE_URL}/training/evaluate", json={
    "question": quiz["question"],
    "selected_answer": correct_val,
    "correct_answer": correct_val,
    "difficulty": "medium",
    "user_id": USER_ID,
    "topic_id": topic_id,
    "topic_name": TOPIC_NAME
})

if eval_resp.status_code == 200:
    fb = eval_resp.json()["feedback"]
    print_result(2, True, f"Feedback received: {fb[:50]}...")
else:
    print_result(2, False, f"Failed: {eval_resp.text}")

# --- SCENARIO 3: Evaluate Incorrect Answer ---
print("\n--- Scenario 3: Evaluate Incorrect Answer ---")
# Pick an answer that is NOT correct. (Assuming options are 1,2,3,4)
wrong_val = "1" if correct_val != "1" else "2"

eval_resp_wrong = requests.post(f"{BASE_URL}/training/evaluate", json={
    "question": quiz["question"],
    "selected_answer": wrong_val,
    "correct_answer": correct_val,
    "difficulty": "medium",
    "user_id": USER_ID,
    "topic_id": topic_id,
    "topic_name": TOPIC_NAME
})

if eval_resp_wrong.status_code == 200:
    fb = eval_resp_wrong.json()["feedback"]
    print_result(3, True, f"Feedback (Wrong) received: {fb[:50]}...")
else:
    print_result(3, False, f"Failed: {eval_resp_wrong.text}")

# --- SCENARIO 4: Check Stats ---
print("\n--- Scenario 4: Verify Stats Update ---")
# We did 1 correct, 1 incorrect. Total 2 quizzes.
stats_resp = requests.get(f"{BASE_URL}/training/stats/{USER_ID}")
if stats_resp.status_code == 200:
    stats = stats_resp.json()
    total = stats["total_quizzes"]
    print(f"   Total Quizzes: {total}, Win Rate: {stats['win_rate']}%")
    if total >= 2: # >= because user might have run other tests with this ID if collision (though unlikely with timestamp)
        print_result(4, True, "Stats updated correctly")
    else:
        print_result(4, False, f"Stats count mismatch: {total}")
else:
    print_result(4, False, f"Failed: {stats_resp.text}")

print("\n" + "="*60)
print("✅ TEST 03 COMPLETE")
