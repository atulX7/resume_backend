import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.cover_letter import CoverLetterRequest, CoverLetterResponse
from app.services.cover_letter_service import generate_cover_letter

router = APIRouter()
logger = logging.getLogger("app")


@router.post("/generate", response_model=CoverLetterResponse)
async def ai_generate_cover_letter(
    request: CoverLetterRequest, db: Session = Depends(get_db)
):
    """Generates a cover letter using AI."""
    logger.info(
        f"Received cover letter generation request for: {request.job_title} at {request.company_name}"
    )

    try:
        response = generate_cover_letter(db, request)
        logger.info(f"Generated cover letter successfully for user: {request.user_id}")
        return response
    except Exception as e:
        logger.error(f"Error generating cover letter: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate cover letter")
