import requests
import json
import time

BASE_URL = "http://localhost:8000"
USER_ID = 102

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
        if isinstance(payload, dict) and "main_arguments" in payload:
            print("  Response Snippet:")
            print(f"    material_id: {payload.get('material_id')}")
            print(f"    topic_id: {payload.get('topic_id')}")
            print(f"    difficulty: {payload.get('difficulty')}")
            print(f"    [+ Lists of generated arguments...]")
        else:
            print(f"  Response: {json.dumps(payload, indent=2)}")
    if not success:
        print("\nStopping tests due to failure.")
        exit(1)

def run_tests():
    print_header("FLOW 02: AI MATERIALS GENERATION")

    try:
        requests.get(f"{BASE_URL}/health")
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Server is not running! Please start uvicorn app.main:app --reload first.")
        return

    # Setup core data quickly
    print("Setting up background topic...")
    cat = requests.post(f"{BASE_URL}/categories/", json={"user_id": USER_ID, "category_name": "History"}).json()
    top = requests.post(f"{BASE_URL}/topics/", json={"user_id": USER_ID, "category_id": cat["category_id"], "topic_name": "The Fall of Rome"}).json()
    topic_id = top["topic_id"]

    # --- Scenario 1: Generate Materials ---
    print_scenario("1", "Generate AI Training Materials (Expected ~5s wait)")
    req_json = {
        "user_id": USER_ID,
        "topic_id": topic_id,
        "topic_name": "The Fall of Rome",
        "description": "Internal decay versus external pressure.",
        "difficulty": 4
    }
    print(f"  Sending POST /topics/{topic_id}/generate-materials")
    print(f"  Payload:\n  {json.dumps(req_json, indent=2)}")
    
    resp = requests.post(f"{BASE_URL}/topics/{topic_id}/generate-materials", json=req_json)
    
    success = resp.status_code == 200
    print_result(success, f"Status {resp.status_code}", resp.json() if success else resp.text)

    print_header("MATERIALS TESTS COMPLETE")

if __name__ == "__main__":
    run_tests()
