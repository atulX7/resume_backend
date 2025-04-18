from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, timezone
from app.database.connection import Base


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    resume_storage_key = Column(String)  # Storage file key
    resume_metadata = Column(
        JSONB, nullable=True, default={}
    )  # Stores structured resume details (name, skills, etc.)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
