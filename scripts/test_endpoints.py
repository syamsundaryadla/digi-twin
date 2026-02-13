"""Full endpoint test for production readiness verification."""
import requests

BASE = "http://127.0.0.1:8000"
results = []

def test(name, r):
    results.append((name, r.status_code))
    return r

# 1. Auth sync
r = test("POST /auth/sync", requests.post(f"{BASE}/auth/sync", json={"email": "localtest@test.com", "full_name": "Local Test"}))
uid = r.json().get("user_id", 0)

# 2. Profile read
test("GET /me/{uid}", requests.get(f"{BASE}/me/{uid}"))

# 3. Profile update
test("PUT /me/{uid}", requests.put(f"{BASE}/me/{uid}", json={"full_name": "Updated Name"}))

# 4. Add memories (onboarding simulation)
test("POST /memories/{uid}", requests.post(f"{BASE}/memories/{uid}", json={"items": ["Likes python", "Enjoys music"]}))

# 5. Get memories
test("GET /memories/{uid}", requests.get(f"{BASE}/memories/{uid}"))

# 6. Create reminder
r = test("POST /reminders/{uid}", requests.post(f"{BASE}/reminders/{uid}", json={"content": "Buy groceries", "due_date": None}))
rid = r.json().get("id", 0)

# 7. Get reminders
test("GET /reminders/{uid}", requests.get(f"{BASE}/reminders/{uid}"))

# 8. Toggle reminder
test("PUT /reminders/toggle", requests.put(f"{BASE}/reminders/{rid}/toggle"))

# 9. Delete reminder
test("DELETE /reminders", requests.delete(f"{BASE}/reminders/{rid}"))

# 10. Chat
r = test("POST /chat", requests.post(f"{BASE}/chat", json={"user_id": uid, "question": "Hi there!", "session_id": None}))
sid = r.json().get("session_id", "")

# 11. Get sessions
test("GET /sessions/{uid}", requests.get(f"{BASE}/sessions/{uid}"))

# 12. Get history
test("GET /history/{sid}", requests.get(f"{BASE}/history/{sid}"))

# Print results
print("=" * 45)
print(f"{'ENDPOINT':<28} {'STATUS':>6}")
print("=" * 45)
all_pass = True
for name, status in results:
    icon = "PASS" if status == 200 else "FAIL"
    if status != 200:
        all_pass = False
    print(f"  {name:<26} {status:>3}  {icon}")
print("=" * 45)
print(f"  Result: {'ALL 12 ENDPOINTS PASSED' if all_pass else 'SOME FAILED'}")
