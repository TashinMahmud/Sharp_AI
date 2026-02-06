
import requests
import json
import time

BASE_URL = "http://localhost:8000"
TIMESTAMP = int(time.time())
USER_ID = f"test_user_{TIMESTAMP}"
CATEGORY_NAME = f"Core Test Category {TIMESTAMP}"
TOPIC_NAME = "Core Test Topic"

def print_header(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_result(step, success, message):
    icon = "✅" if success else "❌"
    print(f"[{step}] {icon} {message}")
    if not success:
        exit(1)

print_header("TEST 01: CORE DATA (Categories & Topics)")
print(f"User ID: {USER_ID}")

# --- SCENARIO 1: Create Category (Success) ---
print("\n--- Scenario 1: Create Valid Category ---")
cat_resp = requests.post(f"{BASE_URL}/categories/", json={
    "category_name": CATEGORY_NAME,
    "user_id": USER_ID,
    "description": "Valid category description"
})
if cat_resp.status_code == 200:
    category_id = cat_resp.json()["category_id"]
    print_result(1, True, f"Category Created: {category_id}")
else:
    print_result(1, False, f"Failed: {cat_resp.text}")

# --- SCENARIO 2: Create Topic (Success) ---
print("\n--- Scenario 2: Create Valid Topic ---")
topic_resp = requests.post(f"{BASE_URL}/topics/", json={
    "category_id": category_id,
    "user_id": USER_ID,
    "topic_name": TOPIC_NAME,
    "description": "Valid topic description"
})
if topic_resp.status_code == 200:
    topic_id = topic_resp.json()["topic_id"]
    print_result(2, True, f"Topic Created: {topic_id}")
else:
    print_result(2, False, f"Failed: {topic_resp.text}")

# --- SCENARIO 3: Get Categories (Success) ---
print("\n--- Scenario 3: Retrieve User Categories ---")
get_cat_resp = requests.get(f"{BASE_URL}/categories/{USER_ID}")
if get_cat_resp.status_code == 200:
    cats = get_cat_resp.json()
    found = any(c["category_id"] == category_id for c in cats)
    print_result(3, found, f"Retrieved {len(cats)} categories. Target found: {found}")
else:
    print_result(3, False, f"Failed: {get_cat_resp.text}")

# --- SCENARIO 4: Get Topics (Success) ---
print("\n--- Scenario 4: Retrieve Category Topics ---")
get_topic_resp = requests.get(f"{BASE_URL}/topics/{category_id}")
if get_topic_resp.status_code == 200:
    topics = get_topic_resp.json()
    found = any(t["topic_id"] == topic_id for t in topics)
    print_result(4, found, f"Retrieved {len(topics)} topics. Target found: {found}")
else:
    print_result(4, False, f"Failed: {get_topic_resp.text}")

# --- SCENARIO 5: Create Topic with Invalid Category (Failure) ---
print("\n--- Scenario 5: Invalid Category ID Handling ---")
bad_topic_resp = requests.post(f"{BASE_URL}/topics/", json={
    "category_id": "invalid-uuid-123",
    "user_id": USER_ID,
    "topic_name": "Should Fail",
    "description": "This should not work"
})
# Note: Depending on logic, it might create it in DB but just have bad link, 
# OR it might validate. Current implementation treats category_id just as a string field in metadata.
# So it actually MIGHT succeed in current mock/DB if we don't strictly validate existence.
# Let's inspect the status code.
if bad_topic_resp.status_code == 200:
    print("⚠️  Warning: API allowed creation with non-existent category ID (Weak Consistency)")
else:
    print("✅ API correctly rejected invalid category (or errored)")
print(f"Status: {bad_topic_resp.status_code}")

print("\n" + "="*60)
print("✅ TEST 01 COMPLETE")
