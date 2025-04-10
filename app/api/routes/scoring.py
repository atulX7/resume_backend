from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.middleware.auth_dependency import get_current_user
from app.schemas.scoring import ResumeScoringResponse
from app.services.scoring_service import score_resume
from app.utils.constants import FEATURE_RESUME_EVAL
from app.utils.plan_usage import check_feature_access

router = APIRouter()


@router.post("/", response_model=ResumeScoringResponse)
async def ai_score_resume(
    resume_file: UploadFile = File(...),  # ✅ Accepts resume file upload
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Scores a resume using AI analysis."""
    check_feature_access(db, current_user.id, FEATURE_RESUME_EVAL)
    return score_resume(resume_file)
