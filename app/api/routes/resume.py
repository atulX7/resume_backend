from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.middleware.auth_dependency import get_current_user
from app.schemas.resume import ResumeResponse
from app.services.resume_service import (
    handle_resume_upload,
    handle_delete_resume,
    get_resume_download_url,
    handle_resume_update,
)
from app.database.resume import get_resumes, get_resume

router = APIRouter()


@router.post("/", response_model=ResumeResponse)
async def upload_resume(
    file: UploadFile = File(...),  # ✅ Accepts file as multipart/form-data
    title: str = Form(...),  # ✅ Extracts title from form-data
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Uploads a new resume and stores metadata in DB."""
    resume = handle_resume_upload(db, current_user.id, file, title)
    return resume


@router.get("/", response_model=list[ResumeResponse])
async def list_resumes(
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """Fetch all resumes of a user."""
    return get_resumes(db, current_user.id)


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume_detail(
    resume_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Fetch a single resume."""
    resume = get_resume(db, resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume


@router.put("/{resume_id}", response_model=ResumeResponse)
async def update_resume_details(
    resume_id: str,
    updated_resume: UploadFile = File(None),
    title: str = Form(None),
    resume_data: str = Form(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update an existing resume."""
    updated_resume_record = handle_resume_update(
        db, resume_id, current_user.id, updated_resume, title, resume_data
    )

    if not updated_resume_record:
        raise HTTPException(status_code=404, detail="Resume not found")

    return updated_resume_record


@router.delete("/{resume_id}")
async def delete_resume_entry(
    resume_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Delete a resume."""
    resume = handle_delete_resume(db, resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return {"message": "Resume deleted successfully"}


@router.get("/{resume_id}/download")
async def download_resume(
    resume_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Generates a downloadable link for a resume."""
    download_url = get_resume_download_url(db, current_user.id, resume_id)
    if not download_url:
        raise HTTPException(status_code=404, detail="Resume not found")

    return {"download_url": download_url}
