import json
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from app.models.resume import Resume
import uuid

def create_resume(db: Session, user_id: str, title: str, s3_url: str):
    """Stores the resume metadata in the database."""
    new_resume = Resume(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title=title,
        s3_url=s3_url,
    )
    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)
    return new_resume

def get_resumes(db: Session, user_id: str):
    return db.query(Resume).filter(Resume.user_id == user_id).all()

def get_resume(db: Session, resume_id: str):
    return db.query(Resume).filter(Resume.id == resume_id).first()

def get_resume_by_id(db: Session, resume_id: str, user_id: str):
    """Fetch resume by ID and user ID"""
    return db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user_id).first()

def update_resume_file(db: Session, resume: Resume, new_s3_url: str):
    """Update resume file URL in the database"""
    resume.s3_url = new_s3_url
    db.commit()

def update_resume_data(db: Session, resume: Resume, title: Optional[str] = None, resume_data: Optional[dict] = None):
    """Updates an existing resume's metadata (title, resume_data)."""

    if title:
        resume.title = title  # ✅ Update title if provided

    if resume_data:
        if not isinstance(resume_data, dict):  # ✅ Ensure resume_data is a dictionary
            try:
                resume_data = json.loads(resume_data)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON format for resume_data")

        updated_resume_data = resume.resume_data or {}  # Ensure it's a dictionary
        updated_resume_data.update(resume_data)  # ✅ Update with new data
        resume.resume_data = updated_resume_data  # ✅ Assign updated JSONB data

        # ✅ Mark the column as modified so SQLAlchemy tracks JSONB changes
        flag_modified(resume, "resume_data")

    db.commit()
    db.refresh(resume)  # ✅ Refresh object with latest DB state
    return resume

def delete_resume(db: Session, resume_id: str):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if resume:
        db.delete(resume)
        db.commit()
    return resume
