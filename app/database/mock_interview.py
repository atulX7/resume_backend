import uuid
from sqlalchemy.orm import Session
from app.models.mock_interview import MockInterviewSession

def create_mock_interview_session(db: Session, user_id: str, job_title: str, job_description: str, resume_s3_url: str):
    """Creates a new mock interview session and stores in DB."""
    session_id = str(uuid.uuid4())
    session = MockInterviewSession(
        id=session_id,
        user_id=user_id,
        job_title=job_title,
        job_description=job_description,
        resume_s3_url=resume_s3_url,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def get_mock_interview_session(db: Session, session_id: str):
    """Fetches an existing mock interview session."""
    return db.query(MockInterviewSession).filter(MockInterviewSession.id == session_id).first()

def update_mock_interview_session(db: Session, session):
    """Updates the mock interview session in DB."""
    db.commit()
    db.refresh(session)
    return session


def update_interview_status(db: Session, session, status):
    session.status = status
    update_mock_interview_session(db, session)


def save_interview_results(db: Session, session, evaluation_results, final_evaluation, status):
    """Saves evaluation results in the database."""
    session.interview_log = evaluation_results
    session.ai_feedback = final_evaluation
    session.status = status
    update_mock_interview_session(db, session)
