from sqlalchemy import Column, String, ForeignKey, DateTime, JSON
from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableList

from app.database.connection import Base

class MockInterviewSession(Base):
    __tablename__ = "mock_interview_sessions"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    job_title = Column(String, nullable=False)
    job_description = Column(String, nullable=False)
    resume_s3_url = Column(String, nullable=False)
    previous_questions = Column(MutableList.as_mutable(JSONB), default=[])  # ✅ Track changes
    interview_log = Column(MutableList.as_mutable(JSONB), default=[])  # ✅ Now tracks changes
    ai_feedback = Column(JSON, default={})  # ✅ AI-generated analysis
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    status = Column(String, default="in_progress")  # "in_progress", "completed"
