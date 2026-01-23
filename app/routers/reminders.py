
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.database import get_db, Reminder

router = APIRouter()

# --- Schemas ---
class ReminderCreate(BaseModel):
    content: str
    due_date: Optional[datetime] = None

class ReminderResponse(BaseModel):
    id: int
    content: str
    due_date: Optional[datetime]
    is_completed: bool
    created_at: datetime

    class Config:
        from_attributes = True

# --- Endpoints ---

@router.get("/reminders/{user_id}", response_model=List[ReminderResponse])
def get_reminders(user_id: int, db: Session = Depends(get_db)):
    return db.query(Reminder).filter(Reminder.user_id == user_id).order_by(Reminder.created_at.desc()).all()

@router.post("/reminders/{user_id}", response_model=ReminderResponse)
def create_reminder(user_id: int, data: ReminderCreate, db: Session = Depends(get_db)):
    reminder = Reminder(user_id=user_id, content=data.content, due_date=data.due_date)
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return reminder

@router.put("/reminders/{reminder_id}/toggle")
def toggle_reminder(reminder_id: int, db: Session = Depends(get_db)):
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    reminder.is_completed = not reminder.is_completed
    db.commit()
    return {"message": "Toggled", "is_completed": reminder.is_completed}

@router.delete("/reminders/{reminder_id}")
def delete_reminder(reminder_id: int, db: Session = Depends(get_db)):
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    db.delete(reminder)
    db.commit()
    return {"message": "Deleted"}
