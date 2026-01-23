import requests
import uuid

BASE_URL = "http://127.0.0.1:8000"

def test_isolation():
    # 1. Signup User A
    uid = uuid.uuid4().hex[:6]
    u1_name = f"userA_{uid}"
    u1_email = f"userA_{uid}@test.com"
    u1_pass = "passA"
    print(f"🔹 Creating User A: {u1_name}...")
    resp = requests.post(f"{BASE_URL}/signup", json={
        "username": u1_name, 
        "email": u1_email, 
        "password": u1_pass,
        "confirm_password": u1_pass
    })
    if resp.status_code != 200:
        print(f"❌ Signup A Failed: {resp.text}")
        return
    u1_id = resp.json()["user_id"]

    # 2. Signup User B
    uid2 = uuid.uuid4().hex[:6]
    u2_name = f"userB_{uid2}"
    u2_email = f"userB_{uid2}@test.com"
    u2_pass = "passB"
    print(f"🔹 Creating User B: {u2_name}...")
    resp = requests.post(f"{BASE_URL}/signup", json={
        "username": u2_name, 
        "email": u2_email, 
        "password": u2_pass,
        "confirm_password": u2_pass
    })
    if resp.status_code != 200:
        print(f"❌ Signup B Failed: {resp.text}")
        return
    u2_id = resp.json()["user_id"]

    # 3. Create Session for A
    print(f"🔹 Creating Session for A...")
    resp = requests.post(f"{BASE_URL}/sessions", json={"user_id": u1_id, "title": "Session A"})
    s1_id = resp.json()["id"]

    # 4. Create Session for B
    print(f"🔹 Creating Session for B...")
    resp = requests.post(f"{BASE_URL}/sessions", json={"user_id": u2_id, "title": "Session B"})
    s2_id = resp.json()["id"]

    # 5. Verify A cannot see B's session
    print(f"🔹 Fetching Sessions for A...")
    resp = requests.get(f"{BASE_URL}/sessions/{u1_id}")
    sessions_a = resp.json()
    ids_a = [s['id'] for s in sessions_a]
    
    if s1_id in ids_a and s2_id not in ids_a:
        print("✅ User A sees Session A and NOT Session B.")
    else:
        print(f"❌ Isolation Fail! A sees: {ids_a}")

    # 6. Verify B cannot see A's session
    print(f"🔹 Fetching Sessions for B...")
    resp = requests.get(f"{BASE_URL}/sessions/{u2_id}")
    sessions_b = resp.json()
    ids_b = [s['id'] for s in sessions_b]

    if s2_id in ids_b and s1_id not in ids_b:
        print("✅ User B sees Session B and NOT Session A.")
    else:
        print(f"❌ Isolation Fail! B sees: {ids_b}")

if __name__ == "__main__":
    try:
        test_isolation()
    except Exception as e:
        print(f"❌ Error: {e}")
