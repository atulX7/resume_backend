import logging
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

logger = logging.getLogger("app")


def handle_resume_upload(db: Session, user_id: str, file: UploadFile, title: str):
    """Handles resume upload and database storage."""
    logger.info(f"[UPLOAD_RESUME] Initiated for user: {user_id}, title: {title}")

    try:
        file_extension = file.filename.split(".")[-1].lower()
        if file_extension not in ["pdf", "doc", "docx", "txt"]:
            logger.warning(f"Unsupported file type: {file.filename}")
            raise ValueError("Invalid file format. Only PDF, DOCX, DOC, and TXT are allowed.")

        s3_url = upload_resume_to_s3(file, user_id)
        resume = create_resume(db, user_id, title, s3_url)

        logger.info(f"[UPLOAD_RESUME] Completed for user: {user_id}, resume_id: {resume.id}")
        return resume

    except Exception as e:
        logger.error(f"[UPLOAD_RESUME] Failed for user: {user_id} - {str(e)}", exc_info=True)
        raise


def handle_delete_resume(db: Session, resume_id: str):
    """Handles deleting a resume from both DB and S3."""
    logger.info(f"[DELETE_RESUME] Initiated for resume_id: {resume_id}")

    try:
        resume = get_resume(db, resume_id)
        if not resume:
            logger.warning(f"[DELETE_RESUME] Resume not found: {resume_id}")
            raise ValueError("Resume not found")

        delete_resume_from_s3(resume.s3_url)
        delete_resume(db, resume_id)

        logger.info(f"[DELETE_RESUME] Successfully deleted resume_id: {resume_id}")
        return {"message": "Resume deleted successfully"}

    except Exception as e:
        logger.error(f"[DELETE_RESUME] Failed for resume_id: {resume_id} - {str(e)}", exc_info=True)
        raise


def get_resume_download_url(db: Session, user_id: str, resume_id: str):
    """Retrieves the S3 URL for downloading a resume."""
    logger.info(f"[DOWNLOAD_URL] Requested by user: {user_id} for resume_id: {resume_id}")

    try:
        resume = get_resume(db, resume_id)
        if not resume or resume.user_id != user_id:
            logger.warning(f"[DOWNLOAD_URL] Resume not found or access denied for resume_id: {resume_id}")
            return None

        url = generate_presigned_url(resume.s3_url)
        logger.info(f"[DOWNLOAD_URL] Generated for resume_id: {resume_id}")
        return url

    except Exception as e:
        logger.error(f"[DOWNLOAD_URL] Failed to generate URL for resume_id: {resume_id} - {str(e)}", exc_info=True)
        return None


def handle_resume_update(
    db: Session,
    resume_id: str,
    user_id: str,
    updated_resume: UploadFile,
    title: str,
    resume_data: str,
):
    """Handles resume updates for file uploads and metadata updates."""
    logger.info(f"[UPDATE_RESUME] Started for user: {user_id}, resume_id: {resume_id}")

    try:
        resume = get_resume_by_id(db, resume_id, user_id)
        if not resume:
            logger.warning(f"[UPDATE_RESUME] Resume not found for update: {resume_id}")
            return None

        if updated_resume:
            logger.info(f"[UPDATE_RESUME] Uploading new resume file for: {resume_id}")
            new_s3_url = upload_resume_to_s3(updated_resume, user_id)
            update_resume_file(db, resume, new_s3_url)

        if title or resume_data:
            logger.info(f"[UPDATE_RESUME] Updating metadata for resume_id: {resume_id}")
            update_resume_data(db, resume, title, resume_data)

        logger.info(f"[UPDATE_RESUME] Completed for resume_id: {resume_id}")
        return {
            "id": resume.id,
            "user_id": resume.user_id,
            "title": resume.title,
            "s3_url": resume.s3_url,
            "resume_data": resume.resume_data,
        }

    except Exception as e:
        logger.error(f"[UPDATE_RESUME] Failed for resume_id: {resume_id} - {str(e)}", exc_info=True)
        raise
