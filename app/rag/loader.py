from langchain_core.documents import Document
from app.database import SessionLocal, UserMemory
import os

def load_user_memory():
    """Load memories from SQL database and local text file, then convert to Documents with metadata."""
    documents = []
    
    # 1. Load from SQL (User-Specific)
    db = SessionLocal()
    try:
        memories = db.query(UserMemory).all()
        for m in memories:
            # Metadata is crucial for filtering later
            doc = Document(
                page_content=m.content,
                metadata={"user_id": m.user_id, "source": "db"}
            )
            documents.append(doc)
    finally:
        db.close()
    
    # 2. Load from user_memory.txt (Generic/Shared)
    # If this is "Raju's Story" and meant for everyone, we might tag it with user_id=None or "all"
    # But usually, if it's user specific, we shouldn't load it for all.
    # For now, let's treat file memory as "Global/Base" context visible to all.
    # To implement "Global", we can use a special ID or just not filter on this doc (if filter is permissive).
    # FAISS filter usually is exact match.
    # Let's assign it to a special "system" user or just duplicating is inefficient.
    # Better approach for RAG: Use filtering in retrieval.
    # If the text file is "Raju's Story" (the persona), it should be available to everyone.
    # Let's give it user_id=0 or -1 to signify global.
    
    file_path = "data/user_memory.txt"
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                file_content = f.read().strip()
                if file_content:
                    doc = Document(
                        page_content=file_content,
                        metadata={"user_id": -1, "source": "file"} # -1 = Global
                    )
                    documents.append(doc)
        except Exception as e:
            print(f"[ERROR] Could not read {file_path}: {e}")

    # If no memories, provide a default one
    if not documents:
        documents = [Document(page_content="System initialized.", metadata={"user_id": -1})]

    return documents

