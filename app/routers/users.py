
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from app.database import get_db, User, UserMemory
from app.routers.chat import reload_rag

router = APIRouter()

# --- Schemas ---
class ProfileUpdate(BaseModel):
    full_name: str

class MemoryResponse(BaseModel):
    id: int
    content: str

# --- Endpoints ---
@router.get("/me/{user_id}")
def get_profile(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"username": user.username, "full_name": user.full_name}

@router.put("/me/{user_id}")
def update_profile(user_id: int, data: ProfileUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.full_name = data.full_name
    db.commit()
    return {"message": "Profile updated", "full_name": user.full_name}

@router.get("/memories/{user_id}", response_model=List[MemoryResponse])
def get_memories(user_id: int, db: Session = Depends(get_db)):
    memories = db.query(UserMemory).filter(UserMemory.user_id == user_id).all()
    return memories

@router.delete("/memories/{memory_id}")
def delete_memory(memory_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    memory = db.query(UserMemory).filter(UserMemory.id == memory_id).first()
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    db.delete(memory)
    db.commit()
    # Trigger RAG reload in background
    background_tasks.add_task(reload_rag)
    return {"message": "Memory deleted"}

class CreateMemoryRequest(BaseModel):
    items: List[str]

@router.post("/memories/{user_id}")
def add_memories(user_id: int, data: CreateMemoryRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Bulk add memories (e.g. from Onboarding)"""
    for content in data.items:
        if content and content.strip():
            db.add(UserMemory(user_id=user_id, content=content.strip()))
    db.commit()
    # Trigger RAG reload in background
    background_tasks.add_task(reload_rag)
    return {"message": "Memories added"}
