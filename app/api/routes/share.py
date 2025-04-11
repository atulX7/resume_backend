import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.middleware.auth_dependency import get_current_user
from app.schemas.share import ResumeShareRequest, ResumeShareResponse
from app.services.share_service import share_resume

router = APIRouter()

logger = logging.getLogger("app")


@router.post("/generate", response_model=ResumeShareResponse)
async def generate_public_resume_link(
    request: ResumeShareRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Generates a public link for a resume."""
    try:
        logger.info(
            f"[SHARE_RESUME] User: {current_user.id} requested shareable link for resume_id: {request.resume_id}"
        )
        response = share_resume(db, request)
        logger.info(
            f"[SHARE_RESUME] Shareable link generated successfully for user: {current_user.id}"
        )
        return response

    except HTTPException as e:
        logger.warning(
            f"[SHARE_RESUME] HTTPException for user: {current_user.id} - {e.detail}"
        )
        raise e

    except Exception as e:
        logger.error(
            f"[SHARE_RESUME] Failed to generate shareable resume link for user: {current_user.id} - {str(e)}"
        )
        raise HTTPException(
            status_code=500, detail="Failed to generate public resume link"
        )
