
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.routers import auth, chat, users, reminders

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load RAG
    # reload_rag()  <-- Disable to speed up boot time for Render (Lazy load instead)
    yield
    # Shutdown

app = FastAPI(title="RepliMate – AI with Memory", lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(users.router)
app.include_router(reminders.router)

# Note: We no longer serve static files from here since we use React on a separate port.
# If we wanted to serve the built React app, we would mount it here.
# For now, we assume dev mode.
