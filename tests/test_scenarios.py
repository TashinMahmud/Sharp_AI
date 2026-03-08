import json
import sys
from fastapi.testclient import TestClient
from app.main import app
import time

# Ensure utf-8 encoding for printing emojis on Windows
sys.stdout.reconfigure(encoding='utf-8')

client = TestClient(app)

USER_ID = 888
SESSION_ID = f"scenario_test_{int(time.time())}"

def print_header(title):
    print(f"\n{'='*70}")
    print(f" {title}")
    print(f"{'='*70}")

def print_scenario(num, desc):
    print(f"\n--- Scenario {num}: {desc} ---")

def print_result(success, message, data=None):
    icon = "✅" if success else "❌"
    print(f"  {icon} {message}")
    if data:
        # format data snippet instead of full dump to keep console clean
        dump = json.dumps(data, indent=2)
        if len(dump) > 300:
            print("  Data snippet:", dump[:300] + "\n  ...[truncated]")
        else:
            print(f"  Data: {dump}")

def run_scenarios():
    print_header("FASTAPI AI QUIZ - BEHAVIORAL SCENARIOS TEST")
    print("Testing edge cases, expected failures, and successful paths.")
    
    # --- CORE DATA ---
    print_header("1. Core Data Validations")
    
    print_scenario("1.1", "Create Valid Category")
    cat_resp = client.post("/categories/", json={
        "category_name": "Scenario Testing",
        "description": "A category for test scenarios",
        "user_id": USER_ID
    })
    success = cat_resp.status_code == 200
    category_id = cat_resp.json().get("category_id") if success else None
    print_result(success, f"Category created. Code: {cat_resp.status_code}", cat_resp.json() if success else cat_resp.text)

    print_scenario("1.2", "Retrieve Non-Existent Categories (Invalid User)")
    bad_cat_resp = client.get("/categories/9999999")
    print_result(bad_cat_resp.status_code == 200, f"Got empty list for fake user. Length: {len(bad_cat_resp.json())}")

    print_scenario("1.3", "Create Valid Topic inside Category")
    top_resp = client.post("/topics/", json={
        "user_id": USER_ID,
        "category_id": category_id,
        "topic_name": "Artificial Intelligence Ethics",
        "description": "Debating AI impact on society."
    })
    success = top_resp.status_code == 200
    topic_id = top_resp.json().get("topic_id") if success else None
    print_result(success, f"Topic created. Code: {top_resp.status_code}", top_resp.json() if success else top_resp.text)

    # --- MATERIALS ---
    print_header("2. AI Materials Generation Engine")
    
    print_scenario("2.1", "Quiz generation before materials exist (Expected 404)")
    early_quiz_resp = client.post("/training/topic-quiz", json={
        "userId": USER_ID,
        "topicId": topic_id,
        "difficulty": 3
    })
    print_result(early_quiz_resp.status_code == 404, f"Properly rejected early quiz request. Code: {early_quiz_resp.status_code}", early_quiz_resp.json())

    print_scenario("2.2", "Generate AI Materials for the Topic")
    mat_resp = client.post(f"/topics/{topic_id}/generate-materials", json={
        "user_id": USER_ID,
        "topic_id": topic_id,
        "topic_name": "Artificial Intelligence Ethics",
        "description": "Debating AI impact on society.",
        "difficulty": 3
    })
    success = mat_resp.status_code == 200
    print_result(success, f"Materials Generated Successfully. Code: {mat_resp.status_code}")

    # --- QUIZ & EVALUATION ---
    print_header("3. Quiz Generation & Evaluation Scenarios")

    print_scenario("3.1", "Topic Quiz Generation (Valid)")
    quiz_resp = client.post("/training/topic-quiz", json={
        "userId": USER_ID,
        "topicId": topic_id,
        "difficulty": 3
    })
    success = quiz_resp.status_code == 200
    quiz_data = quiz_resp.json() if success else None
    print_result(success, f"Quiz Generated. Code: {quiz_resp.status_code}")

    if quiz_data and "question" in quiz_data:
        q_text = quiz_data["question"]
    else:
        q_text = "Unknown question"

    print_scenario("3.2", "Evaluate a completely wrong answer")
    wrong_eval = client.post("/training/evaluate", json={
        "practiceContentId": topic_id,
        "userId": USER_ID,
        "question": q_text,
        "selected_answer": "Batman is the best superhero.",
        "correct_answer": "AI Ethics requires careful legislation.",
        "difficulty": 3
    })
    success = wrong_eval.status_code == 200
    print_result(success, f"Evaluation succeeded (expect low score). Code: {wrong_eval.status_code}", wrong_eval.json() if success else wrong_eval.text)

    # --- DEBATE COACH ---
    print_header("4. Debate Coach Edge Cases")

    print_scenario("4.1", "Debate Coach with Invalid Role Data (Expected 422)")
    bad_debate_resp = client.post("/training/debate", json={
        "userId": USER_ID,
        "session_id": SESSION_ID,
        "topicId": topic_id,
        "difficulty": 3,
        "role": "invalid_magic_role", # Intentional error
        "message": "AI is good."
    })
    print_result(bad_debate_resp.status_code == 422, f"Caught invalid role correctly. Code: {bad_debate_resp.status_code}", bad_debate_resp.json())

    print_scenario("4.2", "Debate Coach Valid Argument")
    good_debate_resp = client.post("/training/debate", json={
        "userId": USER_ID,
        "session_id": SESSION_ID,
        "topicId": topic_id,
        "difficulty": 4,
        "role": "argument", 
        "message": "AI will eventually render all human jobs obsolete, creating severe economic disparities."
    })
    success = good_debate_resp.status_code == 200
    print_result(success, f"Debate Coach Responded. Code: {good_debate_resp.status_code}", good_debate_resp.json() if success else good_debate_resp.text)


    print_header("TEST RUN COMPLETE")

if __name__ == "__main__":
    run_scenarios()
