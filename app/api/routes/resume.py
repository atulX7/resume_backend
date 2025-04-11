import logging
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
logger = logging.getLogger("app")


@router.post("/", response_model=ResumeResponse)
async def upload_resume(
    file: UploadFile = File(...),
    title: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Uploads a new resume and stores metadata in DB."""
    try:
        logger.info(
            f"[RESUME_UPLOAD] Uploading resume for user: {current_user.id}, title: {title}"
        )
        resume = handle_resume_upload(db, current_user.id, file, title)
        logger.info(
            f"[RESUME_UPLOAD] Successfully uploaded resume ID: {resume.id} for user: {current_user.id}"
        )
        return resume
    except Exception as e:
        logger.error(
            f"[RESUME_UPLOAD] Failed to upload resume for user: {current_user.id}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Resume upload failed")


@router.get("/", response_model=list[ResumeResponse])
async def list_resumes(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Fetch all resumes of a user."""
    try:
        logger.info(f"[RESUME_LIST] Fetching resumes for user: {current_user.id}")
        return get_resumes(db, current_user.id)
    except Exception as e:
        logger.error(
            f"[RESUME_LIST] Failed to fetch resumes for user {current_user.id}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Failed to fetch resumes")


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume_detail(
    resume_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Fetch a single resume."""
    logger.info(
        f"[RESUME_DETAIL] Fetching resume ID: {resume_id} for user: {current_user.id}"
    )
    resume = get_resume(db, resume_id)
    if not resume:
        logger.warning(
            f"[RESUME_DETAIL] Resume not found: {resume_id} for user: {current_user.id}"
        )
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
    logger.info(
        f"[RESUME_UPDATE] Updating resume ID: {resume_id} for user: {current_user.id}"
    )
    updated_resume_record = handle_resume_update(
        db, resume_id, current_user.id, updated_resume, title, resume_data
    )

    if not updated_resume_record:
        logger.warning(
            f"[RESUME_UPDATE] Resume not found for update: {resume_id} by user: {current_user.id}"
        )
        raise HTTPException(status_code=404, detail="Resume not found")

    logger.info(
        f"[RESUME_UPDATE] Successfully updated resume ID: {resume_id} for user: {current_user.id}"
    )
    return updated_resume_record


@router.delete("/{resume_id}")
async def delete_resume_entry(
    resume_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Delete a resume."""
    logger.info(
        f"[RESUME_DELETE] Deleting resume ID: {resume_id} for user: {current_user.id}"
    )
    resume = handle_delete_resume(db, resume_id)
    if not resume:
        logger.warning(
            f"[RESUME_DELETE] Resume not found for deletion: {resume_id} for user: {current_user.id}"
        )
        raise HTTPException(status_code=404, detail="Resume not found")

    logger.info(
        f"[RESUME_DELETE] Successfully deleted resume ID: {resume_id} for user: {current_user.id}"
    )
    return {"message": "Resume deleted successfully"}


@router.get("/{resume_id}/download")
async def download_resume(
    resume_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Generates a downloadable link for a resume."""
    logger.info(
        f"[RESUME_DOWNLOAD] Generating download link for resume ID: {resume_id}, user: {current_user.id}"
    )
    download_url = get_resume_download_url(db, current_user.id, resume_id)
    if not download_url:
        logger.warning(
            f"[RESUME_DOWNLOAD] Resume not found for download: {resume_id}, user: {current_user.id}"
        )
        raise HTTPException(status_code=404, detail="Resume not found")

    logger.info(
        f"[RESUME_DOWNLOAD] Resume download URL generated for resume ID: {resume_id}, user: {current_user.id}"
    )
    return {"download_url": download_url}
