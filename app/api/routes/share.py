from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.middleware.auth_dependency import get_current_user
from app.schemas.share import ResumeShareRequest, ResumeShareResponse
from app.services.share_service import share_resume

router = APIRouter()


@router.post("/generate", response_model=ResumeShareResponse)
async def generate_public_resume_link(
    request: ResumeShareRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Generates a public link for a resume."""
    return share_resume(db, request)
