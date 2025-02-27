from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.middleware.auth_dependency import get_current_user
from app.schemas.scoring import ResumeScoringResponse
from app.services.scoring_service import score_resume

router = APIRouter()


@router.post("/", response_model=ResumeScoringResponse)
async def ai_score_resume(
    resume_file: UploadFile = File(...),  # ✅ Accepts resume file upload
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Scores a resume using AI analysis."""
    return score_resume(resume_file)
