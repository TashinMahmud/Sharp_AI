import requests
import json
import time

BASE_URL = "http://localhost:8000"
USER_ID = 103

def print_header(title):
    print(f"\n{'='*70}")
    print(f" {title}")
    print(f"{'='*70}")

def print_scenario(num, desc):
    print(f"\n--- Scenario {num}: {desc} ---")

def print_result(success, message, payload=None):
    icon = "✅ SUCCESS" if success else "❌ FAILED"
    print(f"  {icon} | {message}")
    if payload:
        print(f"  Response: {json.dumps(payload, indent=2)}")
    if not success:
        print("\nStopping tests due to failure.")
        exit(1)

def run_tests():
    print_header("FLOW 03: QUIZ & EVALUATION ENGINE")

    try:
        requests.get(f"{BASE_URL}/health")
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Server is not running! Please start uvicorn app.main:app --reload first.")
        return

    # Setup
    print("Setting up background topic/materials...")
    cat = requests.post(f"{BASE_URL}/categories/", json={"user_id": USER_ID, "category_name": "Economy"}).json()
    top = requests.post(f"{BASE_URL}/topics/", json={"user_id": USER_ID, "category_id": cat["category_id"], "topic_name": "Gold Standard"}).json()
    topic_id = top["topic_id"]
    requests.post(f"{BASE_URL}/topics/{topic_id}/generate-materials", json={"user_id": USER_ID, "topic_id": topic_id, "topic_name": "Gold Standard", "difficulty": 3})

    # --- Scenario 1: Generate Topic Quiz ---
    print_scenario("1", "Generate a Topic Quiz")
    req_json = {
        "userId": USER_ID,
        "topicId": topic_id,
        "difficulty": 3
    }
    print(f"  Sending POST /training/topic-quiz with payload:\n  {json.dumps(req_json, indent=2)}")
    quiz_resp = requests.post(f"{BASE_URL}/training/topic-quiz", json=req_json)
    success = quiz_resp.status_code == 200
    quiz_data = quiz_resp.json() if success else {}
    
    question_text = quiz_data.get("question", "Unknown")
    correct_idx = quiz_data.get("correct_answer", 0)
    options = quiz_data.get("options", [])
    
    # Handle int or str correctly
    if isinstance(correct_idx, int) and len(options) > correct_idx:
        correct_str = options[correct_idx]
    else:
        correct_str = str(correct_idx)

    print_result(success, f"Status {quiz_resp.status_code} | Question: {question_text}", quiz_data)

    # --- Scenario 2: Evaluate Correct Answer ---
    print_scenario("2", "Evaluate a correct answer")
    eval_req = {
        "practiceContentId": topic_id,
        "userId": USER_ID,
        "question": question_text,
        "selected_answer": correct_str,
        "correct_answer": correct_str,
        "difficulty": 3
    }
    print(f"  Sending POST /training/evaluate (Expected High Score) with payload:\n  {json.dumps(eval_req, indent=2)}")
    eval_resp = requests.post(f"{BASE_URL}/training/evaluate", json=eval_req)
    
    success2 = eval_resp.status_code == 200
    print_result(success2, f"Evaluation Status {eval_resp.status_code} | Expected a score close to 1.0", eval_resp.json() if success2 else eval_resp.text)

    # --- Scenario 3: Verify Progress Stats ---
    print_scenario("3", "Verify User Progress Stats updated")
    print(f"  Sending GET /training/stats/{USER_ID}")
    stat_resp = requests.get(f"{BASE_URL}/training/stats/{USER_ID}")
    success3 = stat_resp.status_code == 200
    print_result(success3, f"Stats Status {stat_resp.status_code}", stat_resp.json() if success3 else stat_resp.text)

    print_header("QUIZ TESTS COMPLETE")

if __name__ == "__main__":
    run_tests()
