from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.cover_letter import CoverLetterRequest, CoverLetterResponse
from app.services.cover_letter_service import generate_cover_letter

router = APIRouter()

@router.post("/generate", response_model=CoverLetterResponse)
async def ai_generate_cover_letter(request: CoverLetterRequest, db: Session = Depends(get_db)):
    """Generates a cover letter using AI."""
    return generate_cover_letter(db, request)
