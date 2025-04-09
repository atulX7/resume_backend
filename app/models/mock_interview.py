from sqlalchemy import Column, String, ForeignKey, DateTime, JSON
from datetime import datetime, timezone

from app.database.connection import Base

class MockInterviewSession(Base):
    __tablename__ = "mock_interview_sessions"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    job_title = Column(String, nullable=False)
    job_description_s3_url = Column(String)
    resume_s3_url = Column(String, nullable=False)
    previous_questions_s3_url = Column(String)
    interview_log_s3_url = Column(String)
    ai_feedback_s3_url = Column(String)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    status = Column(String, default="in_progress")  # "in_progress", "completed", "failed"
