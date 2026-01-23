
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import uuid

from app.database import get_db, User
from app.auth import hash_password

router = APIRouter()

# --- Schemas ---
class UserSyncRequest(BaseModel):
    email: str
    username: Optional[str] = None
    full_name: Optional[str] = None

# --- Endpoints ---

@router.post("/auth/sync")
def sync_user(data: UserSyncRequest, db: Session = Depends(get_db)):
    """
    Syncs a user from Supabase Auth to the local 'users' table.
    Returns the local Integer 'user_id' needed for session management.
    And 'is_new_user' flag to trigger onboarding.
    """
    user = db.query(User).filter(User.email == data.email).first()
    is_new = False
    
    if not user:
        is_new = True
        # Create new user in local DB
        # If username not provided (e.g. from generic email login), generate one
        username = data.username or data.email.split("@")[0]
        
        # Ensure username uniqueness
        if db.query(User).filter(User.username == username).first():
            username = f"{username}_{uuid.uuid4().hex[:4]}"

        # Create user with random password (auth is handled by Supabase)
        user = User(
            username=username,
            email=data.email,
            password=hash_password(str(uuid.uuid4())), # Dummy password
            full_name=data.full_name or ""
        )
        db.add(user)
        try:
            db.commit()
        except Exception:
            db.rollback()
            # Fallback retry with new username
            user.username = f"{user.username}_{uuid.uuid4().hex[:4]}"
            db.add(user)
            db.commit()
            
        db.refresh(user)

    return {
        "message": "User synced", 
        "user_id": user.id, 
        "username": user.username,
        "is_new_user": is_new
    }
