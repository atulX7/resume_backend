import logging

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.connection import get_db
from app.middleware.auth_dependency import get_current_user
from app.services.mock_interview_service import (
    start_mock_interview,
    get_mock_interview_sessions_for_user,
    get_mock_interview_session_details,
    update_question_mapping_for_answer, process_mock_interview_worker,
)
from app.schemas.mock_interview import (
    MockInterviewQuestionResponse,
    MockInterviewSessionSummary,
    MockInterviewSessionDetails,
    ProcessingStartedResponse,
)
from app.utils.aws_utils import send_to_mock_interview_queue
from app.utils.constants import FEATURE_MOCK_INTERVIEW
from app.utils.plan_usage import check_feature_access

router = APIRouter()

logger = logging.getLogger("app")


@router.post("/start", response_model=MockInterviewQuestionResponse)
async def start_interview(
    job_title: str = Form(...),
    job_description: str = Form(...),
    resume_temp_key: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Starts a mock interview session and generates all questions in one call."""
    try:
        logger.info(
            f"[MOCK_INTERVIEW_START] Checking access for user: {current_user.id}, job: {job_title}"
        )
        check_feature_access(db, current_user.id, FEATURE_MOCK_INTERVIEW)

        logger.info(
            f"[MOCK_INTERVIEW_START] Initiating mock interview for user: {current_user.id}"
        )
        return start_mock_interview(
            db, current_user.id, job_title, job_description, resume_temp_key
        )
    except Exception as e:
        logger.error(
            f"[MOCK_INTERVIEW_START] Failed to start interview for user {current_user.id}: {e}"
        )
        raise HTTPException(status_code=500, detail="Failed to start mock interview")


@router.post("/{session_id}/process", response_model=ProcessingStartedResponse)
async def process_interview(session_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """
    Processes the mock interview by loading the updated questions mapping (with answer audio file keys)
    from storage and dispatching the session for asynchronous evaluation.
    """
    try:
        logger.info(
            f"[ROUTE] Received process request for session {session_id} by user {current_user.id}"
        )
        payload = {
            "user_id": current_user.id,
            "session_id": session_id,
        }
        if settings.MOCK_DATA:
            logger.info(f"[ROUTE] MOCK mode enabled. Processing interview inline for session {session_id}")
            await process_mock_interview_worker(
                db=db,
                user_id=current_user.id,
                session_id=session_id,
            )
            return {
                "status": "processed",
                "message": "Mock interview processed successfully.",
            }
        else:
            send_to_mock_interview_queue(payload)
            logger.info(f"[ROUTE] Session {session_id} queued successfully for processing")
            return {
                "status": "processing",
                "message": "Your interview is being evaluated. You'll be notified once it's done.",
            }

    except Exception as exc:
        logger.error(
            f"[ROUTE] Error processing session {session_id}: {exc}", exc_info=True
        )
        raise HTTPException(status_code=500, detail="Failed to process interview")


@router.get("/sessions", response_model=list[MockInterviewSessionSummary])
async def get_user_mock_interview_sessions(
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """
    Retrieves a list of all mock interview sessions for a given user.
    """
    try:
        logger.info(
            f"[MOCK_SESSION_LIST] Fetching all sessions for user: {current_user.id}"
        )
        return get_mock_interview_sessions_for_user(db, current_user.id)
    except Exception as e:
        logger.error(
            f"[MOCK_SESSION_LIST] Error fetching sessions for user {current_user.id}: {e}"
        )
        raise HTTPException(
            status_code=500, detail="Failed to fetch mock interview sessions"
        )


@router.get("/sessions/{session_id}", response_model=MockInterviewSessionDetails)
async def get_mock_interview_details(
    session_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Retrieves detailed information about a specific mock interview session.
    """
    try:
        logger.info(
            f"[MOCK_SESSION_DETAIL] Fetching session: {session_id} for user: {current_user.id}"
        )
        return get_mock_interview_session_details(db, session_id)
    except Exception as e:
        logger.error(
            f"[MOCK_SESSION_DETAIL] Error fetching details for session {session_id}: {e}"
        )
        raise HTTPException(status_code=500, detail="Failed to fetch session details")


@router.post("/{session_id}/upload-answer", response_model=dict)
async def upload_answer(
    session_id: str,
    question_id: str = Form(...),
    answer_audio: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Incrementally uploads a candidate's answer audio for a given question.
    This endpoint updates the questions mapping file stored in S3 to include the new answer audio file key.
    """
    try:
        logger.info(
            f"[ROUTE] Received answer upload for session {session_id}, question {question_id}, user {current_user.id}"
        )
        result = await update_question_mapping_for_answer(
            db=db,
            session_id=session_id,
            user_id=current_user.id,
            question_id=question_id,
            answer_audio=answer_audio,
        )
        return result
    except Exception as exc:
        logger.error(
            f"[ROUTE] Error in upload_answer endpoint for session {session_id}: {exc}",
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Failed to upload answer")
