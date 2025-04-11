import logging

from fastapi import APIRouter, Depends, Form, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.middleware.auth_dependency import get_current_user
from app.services.ai_resume_service import tailor_resume
from app.utils.constants import FEATURE_RESUME_TAILOR
from app.utils.plan_usage import check_feature_access

router = APIRouter()

logger = logging.getLogger("app")


@router.post("/tailor")
async def tailor_resume_api(
    job_title: str = Form(...),
    job_description: str = Form(...),
    skills: str = Form(...),  # Comma-separated list of skills
    user_resume: UploadFile = File(...),  # Uploaded resume file
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Tailors a user's resume to a specific job description using AI, providing inline review suggestions."""
    logger.info(
        f"🔍 Checking access for user plan: user_id={current_user.id}, feature={FEATURE_RESUME_TAILOR}"
    )
    try:
        check_feature_access(db, current_user.id, FEATURE_RESUME_TAILOR)
    except Exception as e:
        logger.warning(
            f"⚠️ Feature access denied for user_id={current_user.id}: {str(e)}"
        )
        raise

    logger.info(
        f"🧠 Tailoring resume: user_id={current_user.id}, job_title='{job_title}'"
    )

    # ✅ Call AI resume tailoring service
    tailored_response = tailor_resume(
        db, current_user.id, job_title, job_description, skills, user_resume
    )

    if not tailored_response:
        logger.error(
            f"❌ Failed to tailor resume: user_id={current_user.id}, job_title={job_title}"
        )
        raise HTTPException(status_code=500, detail="Error generating tailored resume")

    logger.info(
        f"✅ Tailored resume generated successfully for user_id={current_user.id}"
    )
    return tailored_response
