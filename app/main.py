# /resume-builder-app
import logging

## Step 1: Poetry Setup
# Run the following commands to create the project
# poetry init -n

# Install dependencies
# poetry install

# To run the application
# poetry run uvicorn app.main:app --reload

## Directory Structure
# The application is structured using modular FastAPI best practices

## main.py - FastAPI Entry Point
from fastapi import FastAPI, Request
from app.api.routes import auth, resume, ai_resume, cover_letter, share, scoring, mock_interview, plans
from app.database.connection import SessionLocal
from app.database.seeder import initialize_db
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import setup_logging

setup_logging()  # Configure logging

# Get a logger for the app
logger = logging.getLogger("app")

app = FastAPI(title="AI Resume Builder API", version="1.0")
logger.info(f"✅ Final ALLOW_ORIGINS: {settings.ALLOW_ORIGINS}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.ALLOW_ORIGINS if origin],  # Change this for production
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Include all API routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(resume.router, prefix="/resumes", tags=["Resumes"])
app.include_router(ai_resume.router, prefix="/ai-resume", tags=["AI Resume"])
# app.include_router(recruiter.router, prefix="/recruiter", tags=["Recruiters"])
app.include_router(cover_letter.router, prefix="/cover-letter", tags=["Cover Letters"])
app.include_router(share.router, prefix="/share", tags=["Public Sharing"])
app.include_router(scoring.router, prefix="/score", tags=["Resume Scoring"])
app.include_router(mock_interview.router, prefix="/mock-interview", tags=["Mock Interviews"])
app.include_router(plans.router, prefix="/plans", tags=["Plans"])

# ✅ Run database seeder at startup
with SessionLocal() as db:
    initialize_db(db)


@app.get("/")
def root():
    return {"message": "AI Resume Builder API is running!"}

import uvicorn
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
