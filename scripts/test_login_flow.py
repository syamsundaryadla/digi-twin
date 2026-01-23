
import requests

BASE_URL = "http://127.0.0.1:8000"

def test_auth():
    print("Testing Signup...")
    signup_data = {
        "username": "testuser_v2",
        "email": "test_v2@example.com",
        "password": "password123",
        "confirm_password": "password123"
    }
    try:
        res = requests.post(f"{BASE_URL}/signup", json=signup_data)
        print(f"Signup Status: {res.status_code}")
        print(f"Signup Resp: {res.text}")
    except Exception as e:
        print(f"Signup Failed: {e}")

    print("\nTesting Login...")
    login_data = {
        "username": "testuser_v2",
        "password": "password123"
    }
    try:
        res = requests.post(f"{BASE_URL}/login", json=login_data)
        print(f"Login Status: {res.status_code}")
        print(f"Login Resp: {res.text}")
    except Exception as e:
        print(f"Login Failed: {e}")

if __name__ == "__main__":
    test_auth()
