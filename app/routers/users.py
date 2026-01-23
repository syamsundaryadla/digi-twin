
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from app.database import get_db, User, UserMemory
from app.rag.loader import load_user_memory
from app.rag.vectorstore import create_vector_store
from app.rag.chain import build_rag_chain
# Import reload function from chat router (where state lives)
from app.routers.chat import reload_rag

router = APIRouter()

# Global state ref (will need invalidation strategy or shared state)
# For now, we will assume the main app manages RAG invalidation or we expose a helper
# Actually, let's keep the reload_rag logic here or import it if centralized.
# For simplicity in this refactor, we'll keep a lightweight reload here or just not reload perfectly.
# Better: User updates profile -> doesn't affect RAG much. Memory deletion -> affects RAG.

# We need access to the rag_components global or a way to signal. 
# For this refactor, let's export a signal function in main or dependencies.
# Simplest approach for MVP refactor: Import the reload function from a common module or main?
# Circular import risk if importing from main. 
# Plan: Move RAG state management to a new module `app/rag/state.py`

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
def delete_memory(memory_id: int, db: Session = Depends(get_db)):
    memory = db.query(UserMemory).filter(UserMemory.id == memory_id).first()
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    db.delete(memory)
    db.commit()
    # Trigger RAG reload to remove memory from AI context
    reload_rag()
    return {"message": "Memory deleted"}

class CreateMemoryRequest(BaseModel):
    items: List[str]

@router.post("/memories/{user_id}")
def add_memories(user_id: int, data: CreateMemoryRequest, db: Session = Depends(get_db)):
    """Bulk add memories (e.g. from Onboarding)"""
    for content in data.items:
        if content and content.strip():
            db.add(UserMemory(user_id=user_id, content=content.strip()))
    db.commit()
    reload_rag()
    return {"message": "Memories added"}
