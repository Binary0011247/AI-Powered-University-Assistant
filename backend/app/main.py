from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager

# --- NEW: Import your routers here ---
from app.routes import users
from app.routes import chat
from app.routes import speech
from app.routes import notifications  # <--- IMPORT THE NEW ROUTE
from app.services.notifications.notifier import check_and_send_notifications
from app.routes import auth  # <--- IMPORT THE NEW ROUTE
from app.routes import admin # <--- ADD admin
from app.routes import ingest 



@asynccontextmanager
async def lifespan(app: FastAPI):
    # What happens when server STARTS
    scheduler = BackgroundScheduler()
    # Check the database every 60 seconds
    scheduler.add_job(check_and_send_notifications, 'interval', seconds=10)
    scheduler.start()
    print("⏰ Background Notification Scheduler Started!")
    yield
    # What happens when server STOPS
    scheduler.shutdown()

# -------------------------------------

# Create FastAPI app
app = FastAPI(title="AI-Powered University Assistant API")

# CORS middleware (allows frontend to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- NEW: Register your routers here ---
app.include_router(users.router)
app.include_router(chat.router)
app.include_router(speech.router)
app.include_router(notifications.router)
app.include_router(auth.router)
# ... inside your app setup ...
app.include_router(admin.router) # <--- ADD THIS
app.include_router(ingest.router)
# ---------------------------------------

# Root endpoint
@app.get("/")
def root():
    return {
        "message": "AI-Powered University Assistant API",
        "status": "running",
        "version": "1.0.0"
    }

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy"}