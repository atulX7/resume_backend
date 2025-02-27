from fastapi import APIRouter, Depends, Form, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.middleware.auth_dependency import get_current_user
from app.services.ai_resume_service import tailor_resume

router = APIRouter()


@router.post("/tailor")
async def tailor_resume_api(
    job_title: str = Form(...),
    job_description: str = Form(...),
    skills: str = Form(...),  # Comma-separated list of skills
    user_resume: UploadFile = File(...),  # Uploaded resume file
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Tailors a user's resume to a specific job description using AI, providing inline review suggestions."""

    # ✅ Call AI resume tailoring service
    tailored_response = tailor_resume(db, current_user.id, job_title, job_description, skills, user_resume)

    if not tailored_response:
        raise HTTPException(status_code=500, detail="Error generating tailored resume")

    return tailored_response