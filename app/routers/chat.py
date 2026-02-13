
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone

from app.database import get_db, User, ChatSession, ChatHistory, UserMemory, Reminder
from app.rag.loader import load_user_memory
from app.rag.vectorstore import create_vector_store
from app.rag.chain import build_rag_chain
import json
import os 
from langchain_google_genai import ChatGoogleGenerativeAI
from dateutil import parser

router = APIRouter()

# --- RAG STATE ---
# Quick local state for MVP refactor. Ideally this is in a singleton class.
rag_components: Dict[str, Any] = {}

def reload_rag():
    print("[INFO] Reloading RAG Memory...")
    try:
        docs = load_user_memory()
        vectorstore = create_vector_store(docs)
        chain = build_rag_chain(vectorstore)
        rag_components["chain"] = chain
        print("[SUCCESS] RAG Memory Reloaded!")
    except Exception as e:
        print(f"[WARN] RAG Reload failed (empty memory?): {e}")

# Initial load
# reload_rag() # Can't do at import time easily, do at startup

# --- Schemas ---
class CreateSessionRequest(BaseModel):
    user_id: int
    title: str = "New Chat"

class SessionResponse(BaseModel):
    id: str
    title: str
    created_at: datetime

class ChatRequest(BaseModel):
    user_id: int
    question: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    role: str
    content: str

# --- Helpers ---
def extract_learning(sentence: str):
    triggers = ["i prefer", "i like", "i don't like", "i do not like", "i want", "i hate", "my name is", "i am"]
    sentence_lower = sentence.lower()
    for trigger in triggers:
        if trigger in sentence_lower:
            return sentence.strip()
    return None

def process_ai_reminder(user_id: int, question: str, db: Session):
    """
    Uses LLM to extract reminder details and adds to DB.
    Returns response string if successful, else None.
    """
    triggers = ["remind me", "set a reminder", "add reminder", "remind"]
    if not any(question.lower().startswith(t) for t in triggers):
        return None

    print(f"[INFO] Detecting Reminder Intent: {question}")
    
    # specialized prompt
    llm = ChatGoogleGenerativeAI(model="models/gemini-2.5-flash", api_key=os.getenv("GOOGLE_API_KEY"), temperature=0)
    
    current_time = datetime.utcnow().isoformat()
    
    prompt = f"""
    Extract reminder details from the user request.
    Current Time (UTC): {current_time}
    User Request: "{question}"
    
    Return ONLY a valid JSON object with keys:
    - "content": (string) what to remind about
    - "due_date": (string) ISO 8601 datetime (YYYY-MM-DDTHH:MM:SS) calculated relative to Current Time. If no time specified, guess reasonable future time (e.g. +1 hour).
    
    Example output: {{"content": "buy milk", "due_date": "2023-10-27T15:00:00"}}
    """
    
    try:
        response = llm.invoke(prompt)
        # cleanup markdown code blocks if any
        text = response.content.replace("```json", "").replace("```", "").strip()
        data = json.loads(text)
        
        content = data.get("content")
        due_date_str = data.get("due_date")
        
        if content and due_date_str:
            # Parse to ensure valid
            due_date = parser.parse(due_date_str)
            # Ensure naive or aware match DB expectations (usually naive UTC in this app)
            if due_date.tzinfo:
                due_date = due_date.astimezone(timezone.utc).replace(tzinfo=None)
            
            reminder = Reminder(user_id=user_id, content=content, due_date=due_date)
            db.add(reminder)
            db.commit()
            
            # Friendly relative response
            diff = due_date - datetime.utcnow()
            minutes = int(diff.total_seconds() / 60)
            time_str = f"in about {minutes} minutes" if minutes > 0 else "soon"
            if minutes >= 60:
                hours = minutes // 60
                mins = minutes % 60
                time_str = f"in {hours}h {mins}m"
            
            return f"I've set a reminder: '{content}' ({time_str})."
            
    except Exception as e:
        print(f"[WARN] Reminder extraction failed: {e}")
        return None  # Fallback to normal chat
    
    return None

# --- Endpoints ---
@router.post("/sessions")
def create_session(data: CreateSessionRequest, db: Session = Depends(get_db)):
    new_session = ChatSession(
        id=str(uuid.uuid4()),
        user_id=data.user_id,
        title=data.title
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

@router.get("/sessions/{user_id}", response_model=List[SessionResponse])
def get_sessions(user_id: int, db: Session = Depends(get_db)):
    sessions = db.query(ChatSession).filter(ChatSession.user_id == user_id).order_by(ChatSession.created_at.desc()).all()
    return sessions

@router.delete("/sessions/{session_id}")
def delete_session(session_id: str, db: Session = Depends(get_db)):
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    db.query(ChatHistory).filter(ChatHistory.session_id == session_id).delete()
    db.delete(session)
    db.commit()
    return {"message": "Session deleted"}

@router.get("/history/{session_id}", response_model=List[ChatResponse])
def get_history(session_id: str, db: Session = Depends(get_db)):
    history = db.query(ChatHistory).filter(ChatHistory.session_id == session_id).order_by(ChatHistory.timestamp.asc()).all()
    return history

@router.post("/chat")
def chat(data: ChatRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # 0. Ensure Session
    session_id = data.session_id
    if not session_id:
        new_sess = ChatSession(id=str(uuid.uuid4()), user_id=data.user_id, title=data.question[:30] + "...")
        db.add(new_sess)
        db.commit()
        session_id = new_sess.id

    # 1. Learning
    new_memory = extract_learning(data.question)
    if new_memory:
        db.add(UserMemory(user_id=data.user_id, content=new_memory))
        db.commit()
        # Trigger RAG reload in background
        background_tasks.add_task(reload_rag)

    # 1.5 Check for Action (Reminder)
    reminder_response = process_ai_reminder(data.user_id, data.question, db)
    if reminder_response:
        # If action taken, return early
        # Also trigger RAG reload because a new reminder exists
        background_tasks.add_task(reload_rag)
        
        db.add(ChatHistory(user_id=data.user_id, session_id=session_id, role="user", content=data.question))
        db.add(ChatHistory(user_id=data.user_id, session_id=session_id, role="assistant", content=reminder_response))
        db.commit()
        return {"answer": reminder_response, "learned": False, "session_id": session_id}

    # 2. RAG
    answer = ""
    
    if "chain" not in rag_components:
        # Check if already loading? For simplicity, just trigger if missing.
        # We use background_tasks to load it so we don't block this request.
        
        background_tasks.add_task(reload_rag)
        answer = "I am initializing my memory system 🧠. Please ask me again in about 30 seconds!"
    
    else:
        user = db.query(User).filter(User.id == data.user_id).first()
        user_name = user.full_name if user and user.full_name else "User"
        try:
            response = rag_components["chain"].invoke({
                "question": data.question, 
                "user_name": user_name,
                "user_id": data.user_id
            })
            answer = response.content
        except Exception as e:
            answer = f"I am having trouble accessing my memory right now. ({str(e)})"

    # 3. Save
    db.add(ChatHistory(user_id=data.user_id, session_id=session_id, role="user", content=data.question))
    db.add(ChatHistory(user_id=data.user_id, session_id=session_id, role="assistant", content=answer))
    db.commit()

    return {"answer": answer, "learned": new_memory is not None, "session_id": session_id}
