from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from app.api import resume, jobs, search
from app.db.session import init_db, test_db_connection
from app.services.scheduler import start_scheduler, stop_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting Job Recommendation Platform...")
    
    try:
        await test_db_connection()
        await init_db()
        start_scheduler()
        print("Application started successfully")
    except Exception as e:
        print(f"CRITICAL ERROR during startup: {e}")
        import traceback
        traceback.print_exc()
        raise
    
    yield
    
    print("Shutting down...")
    stop_scheduler()

app = FastAPI(
    title="Job Recommendation Platform",
    description="Smart job matching with resume-based caching",
    version="2.0.0",
    lifespan=lifespan
)

allowed_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
]

# Split comma-separated frontend URLs from environment variable
frontend_urls = os.getenv("FRONTEND_URL", "")
if frontend_urls:
    allowed_origins.extend([url.strip() for url in frontend_urls.split(",")])

allowed_origins = [origin for origin in allowed_origins if origin]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(resume.router)
app.include_router(jobs.router)
app.include_router(search.router)

@app.get("/")
async def root():
    return {
        "message": "Job Recommendation API",
        "status": "running",
        "version": "2.0.0",
        "endpoints": {
            "parse_resume": "/resume/parse",
            "upload_and_match": "/resume/upload-and-match",
            "health": "/health"
        }
    }

@app.get("/health")
async def health():
    from app.db.session import engine
    from sqlalchemy import text
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "version": "2.0.0",
        "database": db_status
    }