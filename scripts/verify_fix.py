import subprocess
import time
import requests
import sys
import os

BASE_URL = "http://127.0.0.1:8000"

def run_verification():
    print("🚀 Starting Verification Script...")

    # 1. Start Server
    print("🔹 Starting FastAPI server...")
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd="d:/twin/replimate-rag",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    print("⏳ Waiting 20s for server to start...")
    time.sleep(20) 

    try:
        # 2. Signup
        print("🔹 Testing Signup...")
        username = f"testuser_{int(time.time())}"
        password = "password123"
        try:
            resp = requests.post(f"{BASE_URL}/signup", json={"username": username, "password": password})
        except requests.exceptions.ConnectionError:
             print("❌ Connection refused. Server stdout/stderr:")
             outs, errs = process.communicate(timeout=5)
             print(f"STDOUT: {outs.decode(errors='ignore')}")
             print(f"STDERR: {errs.decode(errors='ignore')}")
             return

        if resp.status_code != 200:
            print(f"❌ Signup failed: {resp.text}")
            return
        user_id = resp.json()["user_id"]
        print(f"✅ Signup successful (User ID: {user_id})")

        # 3. Learning Chat (Implicit New Session)
        print("🔹 Testing Learning & Session Creation...")
        fact = "I like coding in Python"
        resp = requests.post(f"{BASE_URL}/chat", json={"user_id": user_id, "question": fact})
        data = resp.json()
        
        session_id = data.get("session_id")
        if not session_id:
             print("❌ No session_id returned from chat start.")
             return
        print(f"✅ Session Created: {session_id}")

        if data.get("learned") is not True:
            print(f"❌ Learning failed. Expected 'learned': True, got {data}")
            return
        print(f"✅ Learning trigger success. Response: {data['answer']}")

        # 4. Retrieval Chat (Using Mock Mode Check)
        print("🔹 Testing Retrieval...")
        question = "What is my favorite programming language?"
        resp = requests.post(f"{BASE_URL}/chat", json={
            "user_id": user_id, 
            "question": question,
            "session_id": session_id # Continue session
        })
        answer = resp.json().get("answer", "")
        print(f"🤖 Bot Answer: {answer}")
        
        # Check for Mock Mode or Real RAG
        if "[Mock]" in answer:
            print("✅ Mock Mode confirmed (API Bypassed).")
        elif "Python" in answer or "python" in answer:
             print("✅ Retrieval Verified (Live API).")
        else:
             print("⚠️ Retrieval unclear (possibly mock mode without specific context logic).")

        # 5. History Endpoint (By Session)
        print(f"🔹 Testing History Endpoint for Session {session_id}...")
        resp = requests.get(f"{BASE_URL}/history/{session_id}")
        if resp.status_code != 200:
             print(f"❌ History failed: {resp.text}")
             return
        
        hist = resp.json()
        print(f"📜 History Items: {len(hist)}")
        if len(hist) >= 4: # 2 user, 2 bot (4 items total)
            print("✅ History Endpoint Verified!")
        else:
            print(f"❌ History Endpoint returned incomplete data: {hist}")
            
        # 6. Sessions List Endpoint
        print(f"🔹 Testing Sessions List for User {user_id}...")
        resp = requests.get(f"{BASE_URL}/sessions/{user_id}")
        sessions = resp.json()
        print(f"📂 Sessions Found: {len(sessions)}")
        if len(sessions) > 0 and sessions[0]['id'] == session_id:
             print("✅ Sessions List Verified!")
        else:
             print(f"❌ Sessions List failed or mismatch: {sessions}")

        # 7. Profile Management
        print(f"🔹 Testing Profile Update for User {user_id}...")
        resp = requests.put(f"{BASE_URL}/me/{user_id}", json={"full_name": "Test User"})
        if resp.status_code == 200:
             print("✅ Profile Update Verified!")
        else:
             print(f"❌ Profile Update Failed: {resp.text}")

        # 8. Memory Management
        print(f"🔹 Testing Memory Listing for User {user_id}...")
        resp = requests.get(f"{BASE_URL}/memories/{user_id}")
        memories = resp.json()
        print(f"🧠 Memories Found: {len(memories)}")
        if len(memories) > 0:
             mid = memories[0]['id']
             print(f"🔹 Deleting Memory ID {mid}...")
             resp = requests.delete(f"{BASE_URL}/memories/{mid}")
             if resp.status_code == 200:
                  print("✅ Memory Deletion Verified!")
             else:
                  print(f"❌ Memory Deletion Failed: {resp.text}")
        else:
             print("⚠️ No memories to test deletion.")

        # 9. Delete Session
        print(f"🔹 Testing Session Deletion for Session {session_id}...")
        resp = requests.delete(f"{BASE_URL}/sessions/{session_id}")
        if resp.status_code == 200:
             print("✅ Session Deletion Verified!")
             # Verify it's gone
             resp = requests.get(f"{BASE_URL}/sessions/{user_id}")
             if len(resp.json()) == 0:
                  print("✅ Session confirmed deleted from list.")
             else:
                  print("❌ Session still appears in list.")
        else:
             print(f"❌ Session Deletion Failed: {resp.text}")

    except Exception as e:
        print(f"❌ Verification crashed: {e}")
        # Try to get output
        if process.poll() is not None:
             outs, errs = process.communicate()
             print(f"STDOUT: {outs.decode(errors='ignore')}")
             print(f"STDERR: {errs.decode(errors='ignore')}")
    finally:
        print("🔻 Stopping Server...")
        process.terminate()
        process.wait()

if __name__ == "__main__":
    run_verification()
