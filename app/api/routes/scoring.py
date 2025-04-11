import logging

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.middleware.auth_dependency import get_current_user
from app.schemas.scoring import ResumeScoringResponse
from app.services.scoring_service import score_resume
from app.utils.constants import FEATURE_RESUME_EVAL
from app.utils.plan_usage import check_feature_access

router = APIRouter()

logger = logging.getLogger("app")


@router.post("/", response_model=ResumeScoringResponse)
async def ai_score_resume(
    resume_file: UploadFile = File(...),  # ✅ Accepts resume file upload
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Scores a resume using AI analysis."""
    try:
        logger.info(f"[RESUME_SCORE] Checking feature access for user: {current_user.id}")
        check_feature_access(db, current_user.id, FEATURE_RESUME_EVAL)

        logger.info(f"[RESUME_SCORE] Scoring resume for user: {current_user.id}, filename: {resume_file.filename}")
        result = score_resume(resume_file)

        logger.info(f"[RESUME_SCORE] Successfully scored resume for user: {current_user.id}")
        return result
    except HTTPException as e:
        logger.warning(f"[RESUME_SCORE] Access denied for user: {current_user.id} - {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"[RESUME_SCORE] Unexpected error scoring resume for user: {current_user.id} - {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing resume score")