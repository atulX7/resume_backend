from sqlalchemy.orm import Session
from fastapi import UploadFile
from app.database.resume import (
    create_resume,
    get_resume,
    delete_resume,
    update_resume_file,
    update_resume_data,
    get_resume_by_id,
)
from app.utils.aws_utils import (
    upload_resume_to_s3,
    delete_resume_from_s3,
    generate_presigned_url,
)


def handle_resume_upload(db: Session, user_id: str, file: UploadFile, title: str):
    """Handles resume upload and database storage."""
    file_extension = file.filename.split(".")[-1].lower()

    if file_extension not in ["pdf", "doc", "docx", "txt"]:
        raise ValueError(
            "Invalid file format. Only PDF, DOCX, DOC, and TXT are allowed."
        )

    # ✅ Upload file to S3
    s3_url = upload_resume_to_s3(file, user_id)

    # ✅ Store resume metadata in DB
    resume = create_resume(db, user_id, title, s3_url)
    return resume


def handle_delete_resume(db: Session, resume_id: str):
    """Handles deleting a resume from both DB and S3."""

    resume = get_resume(db, resume_id)
    if not resume:
        raise ValueError("Resume not found")

    # ✅ Extract S3 file key from URL
    s3_url = resume.s3_url

    # ✅ Delete file from S3
    delete_resume_from_s3(s3_url)

    # ✅ Delete resume from database
    delete_resume(db, resume_id)

    return {"message": "Resume deleted successfully"}


def get_resume_download_url(db: Session, user_id: str, resume_id: str):
    """Retrieves the S3 URL for downloading a resume."""

    resume = get_resume(db, resume_id)
    if not resume or resume.user_id != user_id:
        return None  # Resume not found or belongs to another user

    resume_url = generate_presigned_url(resume.s3_url)
    return resume_url  # Return the S3 public link


def handle_resume_update(
    db: Session,
    resume_id: str,
    user_id: str,
    updated_resume: UploadFile,
    title: str,
    resume_data: str,
):
    """Handles resume updates for file uploads and metadata updates."""

    # ✅ Fetch the resume
    resume = get_resume_by_id(db, resume_id, user_id)
    if not resume:
        return None  # Return None if resume is not found

    # ✅ If a new resume file is provided, upload it and update S3 URL
    if updated_resume:
        new_s3_url = upload_resume_to_s3(updated_resume, user_id)
        update_resume_file(db, resume, new_s3_url)

    # ✅ If title or resume data is provided, update them
    if title or resume_data:
        update_resume_data(db, resume, title, resume_data)

    return {
        "id": resume.id,
        "user_id": resume.user_id,
        "title": resume.title,
        "s3_url": resume.s3_url,
        "resume_data": resume.resume_data,
    }
