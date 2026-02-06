
import requests
import json
import time

BASE_URL = "http://localhost:8000"
TIMESTAMP = int(time.time())
USER_ID = f"test_user_mat_{TIMESTAMP}"
CATEGORY_NAME = f"Material Test Cat {TIMESTAMP}"
TOPIC_NAME = "Machine Learning"

def print_header(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_result(step, success, message):
    icon = "✅" if success else "❌"
    print(f"[{step}] {icon} {message}")
    if not success:
        exit(1)

print_header("TEST 02: MATERIAL GENERATION (Valid & Edge Cases)")

# PRE-REQUISITE: Create Data
print("\n--- Setup: Creating Category & Topic ---")
cat_resp = requests.post(f"{BASE_URL}/categories/", json={"category_name": CATEGORY_NAME, "user_id": USER_ID})
category_id = cat_resp.json()["category_id"]

topic_resp = requests.post(f"{BASE_URL}/topics/", json={
    "category_id": category_id, "user_id": USER_ID, "topic_name": TOPIC_NAME
})
topic_id = topic_resp.json()["topic_id"]
print(f"Prefix: Topic ID {topic_id}")

# --- SCENARIO 1: Generate Standard Materials (Medium) ---
print("\n--- Scenario 1: Generate Materials (Medium Difficulty) ---")
start_time = time.time()
mat_resp = requests.post(f"{BASE_URL}/materials/generate", json={
    "topic_id": topic_id,
    "user_id": USER_ID
})
duration = time.time() - start_time

if mat_resp.status_code == 200:
    data = mat_resp.json()
    count = len(data["main_arguments"])
    if count > 0 and data["difficulty"] == "medium":
        print_result(1, True, f"Generated {count} arguments in {duration:.2f}s")
    else:
        print_result(1, False, "Empty arguments or wrong difficulty")
else:
    print_result(1, False, f"Failed: {mat_resp.text}")

# --- SCENARIO 2: Retrieve Materials ---
print("\n--- Scenario 2: Retrieve Saved Materials ---")
get_mat_resp = requests.get(f"{BASE_URL}/materials/{topic_id}")
if get_mat_resp.status_code == 200:
    data = get_mat_resp.json()
    if data["topic_id"] == topic_id:
        print_result(2, True, "Materials retrieved successfully from DB")
    else:
        print_result(2, False, "Mismatch in topic ID")
else:
    print_result(2, False, f"Failed: {get_mat_resp.text}")

# --- SCENARIO 3: Generate Duplicate (Should Update or Fail?) ---
# The logic usually overwrites or adds. Let's see. 
# We'll treat it as a success if it returns 200.
print("\n--- Scenario 3: Re-Generate Materials (Idempotency) ---")
mat_resp_2 = requests.post(f"{BASE_URL}/materials/generate", json={
    "topic_id": topic_id,
    "user_id": USER_ID
})
if mat_resp_2.status_code == 200:
    print_result(3, True, "Re-generation successful (Overwrite/Update behavior)")
else:
    print_result(3, False, "Re-generation failed")

# --- SCENARIO 4: Generate for Non-Existent Topic ---
print("\n--- Scenario 4: Generate for Invalid Topic ID ---")
bad_resp = requests.post(f"{BASE_URL}/materials/generate", json={
    "topic_id": "invalid-uuid-999",
    "user_id": USER_ID
})
if bad_resp.status_code == 404:
    print_result(4, True, "Correctly returned 404 for missing topic")
else:
    print(f"Response: {bad_resp.status_code}")
    print_result(4, False, "API did not return 404 for invalid topic")

print("\n" + "="*60)
print("✅ TEST 02 COMPLETE")
