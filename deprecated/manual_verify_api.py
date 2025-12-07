import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_api():
    print("Checking Health...")
    try:
        res = requests.get(f"{BASE_URL}/healthz")
        print(f"Health: {res.status_code} {res.json()}")
    except Exception as e:
        print(f"Server not ready: {e}")
        return

    print("\nCreating Session...")
    res = requests.post(f"{BASE_URL}/v1/sessions", json={"user_id": "manual_user", "client_type": "script"})
    print(f"Create Session: {res.status_code}")
    if res.status_code != 200:
        print(res.text)
        return
    session_id = res.json()["session_id"]
    print(f"Session ID: {session_id}")

    print("\nSending Message: 'What is my balance?'")
    res = requests.post(f"{BASE_URL}/v1/messages", json={"session_id": session_id, "text": "What is my balance?"})
    print(f"Message Response: {res.status_code}")
    print(json.dumps(res.json(), indent=2))

    print("\nSending Message: 'Block my card'")
    res = requests.post(f"{BASE_URL}/v1/messages", json={"session_id": session_id, "text": "Block my card"})
    print(f"Block Request Response: {res.status_code}")
    print(json.dumps(res.json(), indent=2))
    
    print("\nConfirming Action...")
    res = requests.post(f"{BASE_URL}/v1/actions/confirm", json={"session_id": session_id, "confirmation": "yes"})
    print(f"Confirm Response: {res.status_code}")
    print(json.dumps(res.json(), indent=2))

if __name__ == "__main__":
    # Wait a bit for server to start
    time.sleep(2)
    test_api()
