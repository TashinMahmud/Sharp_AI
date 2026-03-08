import requests
import json
import time

BASE_URL = "http://localhost:8000"
USER_ID = 101

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
    print_header("FLOW 01: CORE DATA (CATEGORIES & TOPICS)")
    
    try:
        requests.get(f"{BASE_URL}/health")
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Server is not running! Please start uvicorn app.main:app --reload first.")
        return

    # --- Scenario 1: Create Category ---
    print_scenario("1", "Create a new Category")
    req_json = {
        "user_id": USER_ID,
        "category_name": "Philosophy",
        "description": "Exploration of fundamental questions."
    }
    print(f"  Sending POST /categories/ with payload:\n  {json.dumps(req_json, indent=2)}")
    resp = requests.post(f"{BASE_URL}/categories/", json=req_json)
    success = resp.status_code == 200
    category_id = resp.json().get("category_id") if success else None
    print_result(success, f"Status {resp.status_code}", resp.json() if success else resp.text)

    # --- Scenario 2: Get Categories ---
    print_scenario("2", f"Retrieve Categories for User {USER_ID}")
    print(f"  Sending GET /categories/{USER_ID}")
    resp = requests.get(f"{BASE_URL}/categories/{USER_ID}")
    print_result(resp.status_code == 200, f"Status {resp.status_code}", resp.json() if resp.status_code == 200 else resp.text)

    # --- Scenario 3: Create Topic ---
    print_scenario("3", "Create a new Topic inside the Category")
    req_json = {
        "user_id": USER_ID,
        "category_id": category_id,
        "topic_name": "Utilitarianism vs Deontology",
        "description": "Debating moral frameworks."
    }
    print(f"  Sending POST /topics/ with payload:\n  {json.dumps(req_json, indent=2)}")
    resp = requests.post(f"{BASE_URL}/topics/", json=req_json)
    print_result(resp.status_code == 200, f"Status {resp.status_code}", resp.json() if resp.status_code == 200 else resp.text)

    print_header("CORE DATA TESTS COMPLETE")

if __name__ == "__main__":
    run_tests()
