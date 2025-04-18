from sqlalchemy import Column, String, ForeignKey, DateTime
from datetime import datetime, timezone

from app.database.connection import Base


class MockInterviewSession(Base):
    __tablename__ = "mock_interview_sessions"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    job_title = Column(String, nullable=False)
    job_description_storage_key = Column(String)
    resume_storage_key = Column(String, nullable=False)
    questions_mapping_storage_key = Column(String)
    interview_log_storage_key = Column(String)
    ai_feedback_storage_key = Column(String)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    status = Column(
        String, default="in_progress"
    )  # "in_progress", "completed", "failed"
