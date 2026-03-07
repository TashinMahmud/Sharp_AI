import json
from fastapi.testclient import TestClient
from app.main import app
import logging

logging.getLogger("httpx").setLevel(logging.WARNING)

client = TestClient(app)

def run_tests():
    print("\n=== Testing /topics ===")
    res = client.post("/topics", json={
        "user_id": 1,
        "topic_name": "Corporate Taxes",
        "description": "Debating whether corporate tax cuts benefit the working class."
    })
    topic_data = res.json()
    print(json.dumps(topic_data, indent=2))
    
    if "topic_id" not in topic_data:
        print("Failed to get topic_id")
        return
        
    topic_id = topic_data["topic_id"]

    print(f"\n=== Testing /materials/generate for Topic ID: {topic_id} ===")
    res = client.post("/materials/generate", json={
        "topicId": topic_id,
        "userId": 1
    })
    material_data = res.json()
    print("Materials generated.")
    # (Print omitted because it can be quite large, just print keys)
    if isinstance(material_data, dict):
        print("Keys:", material_data.keys())

    print("\n=== Testing /training/debate ===")
    res = client.post("/training/debate", json={
        "userId": 1,
        "session_id": "test_sess_123",
        "topicId": topic_id,
        "difficulty": 3,
        "role": "argument",
        "message": "Tax cuts for corporations just lead to stock buybacks, not wage increases for average workers."
    })
    debate_data = res.json()
    print(json.dumps(debate_data, indent=2))

if __name__ == "__main__":
    run_tests()
