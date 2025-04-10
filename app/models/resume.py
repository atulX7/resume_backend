from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, timezone
from app.database.connection import Base


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    s3_url = Column(String, nullable=False)  # S3 Storage Path
    resume_data = Column(
        JSONB, nullable=True, default={}
    )  # Stores structured resume details (name, skills, etc.)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
