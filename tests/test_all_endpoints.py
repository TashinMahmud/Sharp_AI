import json
import sys
from fastapi.testclient import TestClient
from app.main import app

# Ensure utf-8 encoding for printing emojis on Windows
sys.stdout.reconfigure(encoding='utf-8')

client = TestClient(app)

USER_ID = 999
SESSION_ID = "manual_test_session_001"

def print_header(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_result(step, success, message, data=None):
    icon = "[PASS]" if success else "[FAIL]"
    print(f"[{step}] {icon} {message}")
    if data:
        print(json.dumps(data, indent=2))
    if not success:
        print("\nStopping tests due to failure.")
        sys.exit(1)

def run_tests():
    print_header("FASTAPI AI QUIZ - MASTER TEST SUITE")
    print("This script tests all Prisma-aligned endpoints using TestClient.")
    
    # 0. Health
    resp = client.get("/health")
    print_result("0", resp.status_code == 200, "Server Internal TestClient is active")

    # 1. Create Category
    print_header("1. Core Data: Categories & Topics")
    cat_resp = client.post("/categories/", json={
        "category_name": "Test Science",
        "description": "Science topics",
        "user_id": USER_ID
    })
    category_id = cat_resp.json().get("category_id") if cat_resp.status_code == 200 else None
    print_result("1.1", cat_resp.status_code == 200, f"Create Category (ID: {category_id})")

    # 1.2 Create Topic
    top_resp = client.post("/topics/", json={
        "user_id": USER_ID,
        "category_id": category_id,
        "topic_name": "Nuclear Fusion vs Fission",
        "description": "The future of clean energy."
    })
    topic_id = top_resp.json().get("topic_id") if top_resp.status_code == 200 else None
    print_result("1.2", top_resp.status_code == 200, f"Create Topic (ID: {topic_id})")

    # 2. Materials Generation
    print_header("2. AI Material Generation")
    print(f"Generating materials for topic {topic_id} (This takes ~5 seconds)...")
    mat_resp = client.post(f"/topics/{topic_id}/generate-materials", json={
        "user_id": USER_ID,
        "topic_id": topic_id,
        "topic_name": "Nuclear Fusion vs Fission",
        "description": "The future of clean energy.",
        "difficulty": 3
    })
    material_data = mat_resp.json() if mat_resp.status_code == 200 else None
    
    # Format the print block to avoid overwhelming console output
    if mat_resp.status_code == 200:
        keys_only = {"Keys Returned": list(material_data.keys()), "Generated Materials": "Successfully Saved in ChromaDB."}
    else:
        keys_only = material_data
        
    print_result("2.1", mat_resp.status_code == 200, "Generate Materials", keys_only)

    # 3. Quizzes & Evaluation
    print_header("3. AI Quizzes & Evaluation")
    
    # 3.1 Topic Quiz
    print("Generating a quiz specifically for this topic...")
    quiz_resp = client.post("/training/topic-quiz", json={
        "userId": USER_ID,
        "topicId": topic_id,
        "difficulty": 3
    })
    quiz_data = quiz_resp.json() if quiz_resp.status_code == 200 else None
    print_result("3.1", quiz_resp.status_code == 200, "Topic Quiz Generated", quiz_data)

    if quiz_data and "question" in quiz_data:
        q_text = quiz_data["question"]
        options = quiz_data.get("options", [])
        correct_index = quiz_data.get("correct_answer", 0)
        # Handle correct_answer being an index or a string literal
        if isinstance(correct_index, int) and len(options) > correct_index:
            correct_answer = options[correct_index]
        else:
            correct_answer = str(correct_index)
    else:
        print_result("3.1", False, "Quiz data malformed.")
    
    # 3.2 Evaluate Answer
    print(f"\nEvaluating a correct answer for: '{q_text}'")
    eval_resp = client.post("/training/evaluate", json={
        "practiceContentId": topic_id,
        "userId": USER_ID,
        "question": q_text,
        "selected_answer": correct_answer,
        "correct_answer": correct_answer,
        "difficulty": 3
    })
    print_result("3.2", eval_resp.status_code == 200, "Evaluate Correct Answer", eval_resp.json() if eval_resp.status_code == 200 else eval_resp.text)

    # 4. Debate Coach
    print_header("4. AI Debate Coach")
    print("Sending an argument to the Conservative Debate Coach...")
    debate_resp = client.post("/training/debate", json={
        "userId": USER_ID,
        "session_id": SESSION_ID,
        "topicId": topic_id,
        "difficulty": 4,
        "role": "argument",
        "message": "Nuclear fusion is too expensive and complex; we should just focus on expanding solar arrays across the country."
    })
    print_result("4.1", debate_resp.status_code == 200, "Debate Coach Response", debate_resp.json() if debate_resp.status_code == 200 else debate_resp.text)

    # 5. Progress Stats
    print_header("5. Usage & Progress Tracking")
    stats_resp = client.get(f"/training/stats/{USER_ID}")
    print_result("5.1", stats_resp.status_code == 200, "Fetch Usage Stats", stats_resp.json() if stats_resp.status_code == 200 else stats_resp.text)

    print("\n🎉 ALL TESTS PASSED! The Prisma-aligned FastAPI backend is fully operational.")

if __name__ == "__main__":
    run_tests()
