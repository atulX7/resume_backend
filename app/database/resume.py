import json
import logging
import uuid
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from app.models.resume import Resume

logger = logging.getLogger("app")


def create_resume(db: Session, user_id: str, title: str, s3_url: str):
    """Stores the resume metadata in the database."""
    resume_id = str(uuid.uuid4())
    logger.info(f"[RESUME] Creating new resume for user: {user_id} with title: '{title}'")
    new_resume = Resume(
        id=resume_id,
        user_id=user_id,
        title=title,
        s3_url=s3_url,
    )
    try:
        db.add(new_resume)
        db.commit()
        db.refresh(new_resume)
        logger.info(f"[RESUME] Resume created successfully with ID: {resume_id}")
        return new_resume
    except Exception as e:
        logger.error(f"[RESUME] Failed to create resume for user: {user_id}. Error: {str(e)}")
        raise


def get_resumes(db: Session, user_id: str):
    logger.info(f"[RESUME] Fetching all resumes for user: {user_id}")
    try:
        return db.query(Resume).filter(Resume.user_id == user_id).all()
    except Exception as e:
        logger.error(f"[RESUME] Failed to fetch resumes for user: {user_id}. Error: {str(e)}")
        raise


def get_resume(db: Session, resume_id: str):
    logger.info(f"[RESUME] Fetching resume with ID: {resume_id}")
    try:
        return db.query(Resume).filter(Resume.id == resume_id).first()
    except Exception as e:
        logger.error(f"[RESUME] Failed to fetch resume ID: {resume_id}. Error: {str(e)}")
        raise


def get_resume_by_id(db: Session, resume_id: str, user_id: str):
    logger.info(f"[RESUME] Fetching resume ID: {resume_id} for user: {user_id}")
    try:
        return db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user_id).first()
    except Exception as e:
        logger.error(f"[RESUME] Failed to fetch resume for user: {user_id}. Error: {str(e)}")
        raise


def update_resume_file(db: Session, resume: Resume, new_s3_url: str):
    logger.info(f"[RESUME] Updating S3 URL for resume ID: {resume.id}")
    try:
        resume.s3_url = new_s3_url
        db.commit()
        logger.info(f"[RESUME] S3 URL updated for resume ID: {resume.id}")
    except Exception as e:
        logger.error(f"[RESUME] Failed to update S3 URL for resume ID: {resume.id}. Error: {str(e)}")
        raise


def update_resume_data(
    db: Session,
    resume: Resume,
    title: Optional[str] = None,
    resume_data: Optional[dict] = None,
):
    """Updates an existing resume's metadata (title, resume_data)."""
    logger.info(f"[RESUME] Updating resume metadata for ID: {resume.id}")

    try:
        if title:
            resume.title = title
            logger.info(f"[RESUME] Title updated to: {title}")

        if resume_data:
            if not isinstance(resume_data, dict):
                try:
                    resume_data = json.loads(resume_data)
                except json.JSONDecodeError:
                    logger.error("[RESUME] Invalid JSON format for resume_data")
                    raise ValueError("Invalid JSON format for resume_data")

            updated_resume_data = resume.resume_data or {}
            updated_resume_data.update(resume_data)
            resume.resume_data = updated_resume_data
            flag_modified(resume, "resume_data")
            logger.info(f"[RESUME] Resume data updated for ID: {resume.id}")

        db.commit()
        db.refresh(resume)
        logger.info(f"[RESUME] Resume successfully updated for ID: {resume.id}")
        return resume

    except Exception as e:
        logger.error(f"[RESUME] Failed to update resume ID: {resume.id}. Error: {str(e)}")
        raise


def delete_resume(db: Session, resume_id: str):
    logger.info(f"[RESUME] Deleting resume ID: {resume_id}")
    try:
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if resume:
            db.delete(resume)
            db.commit()
            logger.info(f"[RESUME] Resume ID: {resume_id} deleted successfully")
        else:
            logger.warning(f"[RESUME] Resume ID: {resume_id} not found for deletion")
        return resume
    except Exception as e:
        logger.error(f"[RESUME] Failed to delete resume ID: {resume_id}. Error: {str(e)}")
        raise
