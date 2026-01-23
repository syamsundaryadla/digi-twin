import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

def migrate():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        print("[INFO] Checking if 'email' column exists...")
        try:
            # Attempt to select the column to see if it exists
            conn.execute(text("SELECT email FROM users LIMIT 1"))
            print("[INFO] 'email' column already exists. Skipping migration.")
        except Exception:
            print("[INFO] 'email' column missing. Adding it now...")
            # If it fails, the column doesn't exist (likely). Rollback transaction if needed implicitly or just proceed.
            # In some setups, failing a statement aborts the transaction. 
            # Ideally verify via schema info, but direct ALTER is robust if we catch duplicate errors.
            pass

    # Re-connect for the ALTER command to ensure clean transaction state
    with engine.connect() as conn:
        # Commit any previous transaction state
        conn.commit() 
        try:
            print("[INFO] Adding 'email' column to 'users' table...")
            conn.execute(text("ALTER TABLE users ADD COLUMN email VARCHAR UNIQUE"))
            conn.commit()
            print("[SUCCESS] Migration successful: 'email' column added.")
        except Exception as e:
            if "already exists" in str(e):
                 print("[INFO] Column already exists (caught error).")
            else:
                print(f"[ERROR] Migration failed: {e}")

if __name__ == "__main__":
    migrate()
