import logging

from sqlalchemy.orm import Session
from app.models.mock_interview import MockInterviewSession

logger = logging.getLogger("app")


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
    logger.info(
        f"[CREATE_SESSION] Creating mock interview session for user: {user_id}, session_id: {session_id}, job: {job_title}"
    )
    try:
        session = MockInterviewSession(
            id=session_id,
            user_id=user_id,
            job_title=job_title,
            job_description_s3_url=jd_s3_url,
            resume_s3_url=resume_s3_url,
            previous_questions_s3_url=prev_question_s3_url,
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        logger.info(f"[CREATE_SESSION] Successfully created session: {session_id}")
        return session
    except Exception as e:
        logger.error(
            f"[CREATE_SESSION] Failed to create session: {session_id} for user: {user_id} | Error: {str(e)}"
        )
        raise


def get_mock_interview_session(db: Session, session_id: str):
    """Fetches an existing mock interview session."""
    logger.info(f"[FETCH_SESSION] Retrieving mock interview session: {session_id}")
    try:
        session = (
            db.query(MockInterviewSession)
            .filter(MockInterviewSession.id == session_id)
            .first()
        )
        if not session:
            logger.warning(f"[FETCH_SESSION] No session found for ID: {session_id}")
        return session
    except Exception as e:
        logger.error(
            f"[FETCH_SESSION] Error retrieving session {session_id} | Error: {str(e)}"
        )
        raise


def get_mock_interview_sessions_by_user(db: Session, user_id: str):
    """Fetches an existing mock interview session."""
    logger.info(f"[FETCH_ALL_SESSIONS] Retrieving all sessions for user: {user_id}")
    try:
        sessions = (
            db.query(MockInterviewSession)
            .filter(MockInterviewSession.user_id == user_id)
            .all()
        )
        logger.info(
            f"[FETCH_ALL_SESSIONS] Found {len(sessions)} sessions for user: {user_id}"
        )
        return sessions
    except Exception as e:
        logger.error(
            f"[FETCH_ALL_SESSIONS] Error retrieving sessions for user: {user_id} | Error: {str(e)}"
        )
        raise


def save_interview_results(
    db: Session, session, interview_log_s3_url, ai_feedback_s3_url, status
):
    """Saves evaluation results in the database."""
    logger.info(
        f"[SAVE_RESULTS] Saving results for session: {session.id} | Status: {status}"
    )
    try:
        session.interview_log_s3_url = interview_log_s3_url
        session.ai_feedback_s3_url = ai_feedback_s3_url
        session.status = status
        db.commit()
        db.refresh(session)
        logger.info(
            f"[SAVE_RESULTS] Successfully updated results for session: {session.id}"
        )
        return session
    except Exception as e:
        logger.error(
            f"[SAVE_RESULTS] Failed to update results for session: {session.id} | Error: {str(e)}"
        )
        raise
