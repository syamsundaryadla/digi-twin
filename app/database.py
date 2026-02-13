from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from datetime import datetime
import uuid

import os
from dotenv import load_dotenv

load_dotenv()

# Use environment variable or fallback to local SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./replimate_v2.db")

# Handle Render/Supabase Postgres URL quirks (postgres:// -> postgresql://)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

print(f"[DEBUG] Active Database URL: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}")

# Connect args: SQLite needs check_same_thread=False, Postgres does not
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

engine = create_engine(
    DATABASE_URL, connect_args=connect_args
)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True) # New field
    full_name = Column(String, default="") 
    password = Column(String)


class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, index=True)
    title = Column(String, default="New Chat")
    created_at = Column(DateTime, default=datetime.utcnow)


class ChatHistory(Base):
    __tablename__ = "chat_history"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    session_id = Column(String, index=True) # Link to ChatSession
    role = Column(String)
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

class UserMemory(Base):
    __tablename__ = "user_memory"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    content = Column(Text)

class Reminder(Base):
    __tablename__ = "reminders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    content = Column(String)
    due_date = Column(DateTime, nullable=True) # New field
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)




Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_all_memories():
    """Retrieve all user memories from the database locally for RAG loading."""
    db = SessionLocal()
    try:
        memories = db.query(UserMemory).all()
        return [m.content for m in memories]
    finally:
        db.close()


