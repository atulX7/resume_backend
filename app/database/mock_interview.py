import uuid
from sqlalchemy.orm import Session
from app.models.mock_interview import MockInterviewSession


def create_mock_interview_session(
        db: Session, 
        session_id: str, 
        user_id: str, 
        job_title: str, 
        jd_s3_url: str, 
        resume_s3_url: str,
        prev_question_s3_url: str,
):
    """Creates a new mock interview session and stores in DB."""
    session = MockInterviewSession(
        id=session_id,
        user_id=user_id,
        job_title=job_title,
        job_description_s3_url=jd_s3_url,
        resume_s3_url=resume_s3_url,
        previous_questions_s3_url = prev_question_s3_url,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_mock_interview_session(db: Session, session_id: str):
    """Fetches an existing mock interview session."""
    return db.query(MockInterviewSession).filter(MockInterviewSession.id == session_id).first()

def get_mock_interview_sessions_by_user(db: Session, user_id: str):
    """Fetches an existing mock interview session."""
    return db.query(MockInterviewSession).filter(MockInterviewSession.user_id == user_id).all()


def save_interview_results(db: Session, session, user_id, evaluation_results_s3, final_evaluation_s3, status):
    """Saves evaluation results in the database."""
    session.interview_log_s3_url = evaluation_results_s3
    session.ai_feedback_s3_url = final_evaluation_s3
    session.status = status
    db.commit()
    db.refresh(session)
    return session
