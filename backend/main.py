from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from database import init_db
from routers import packages
from scheduler import start_scheduler, stop_scheduler, get_scheduler_status

app = FastAPI(
    title="GLCC - Global Logistics Command Center",
    description="Self-hosted platform for tracking deliveries worldwide",
    version="0.1.0"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database and scheduler on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    # Start scheduler with 1-hour interval (configurable via env)
    interval_hours = int(os.getenv("SCHEDULER_INTERVAL_HOURS", "1"))
    start_scheduler(interval_hours=interval_hours)

# Stop scheduler on shutdown
@app.on_event("shutdown")
async def shutdown_event():
    stop_scheduler()

# Include routers
app.include_router(packages.router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to GLCC - Global Logistics Command Center",
        "status": "operational",
        "version": "0.1.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/scheduler/status")
async def scheduler_status():
    """Get scheduler status and next run times"""
    return get_scheduler_status()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
