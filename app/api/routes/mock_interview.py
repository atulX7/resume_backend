import ast
import logging

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.middleware.auth_dependency import get_current_user
from app.services.mock_interview_service import (
    start_mock_interview,
    get_mock_interview_sessions_for_user,
    get_mock_interview_session_details,
    get_audio_file_map,
)
from app.schemas.mock_interview import (
    MockInterviewQuestionResponse,
    MockInterviewSessionSummary,
    MockInterviewSessionDetails,
    ProcessingStartedResponse,
)
from app.utils.constants import FEATURE_MOCK_INTERVIEW
from app.utils.plan_usage import check_feature_access

router = APIRouter()

logger = logging.getLogger("app")


@router.post("/start", response_model=MockInterviewQuestionResponse)
async def start_interview(
    job_title: str = Form(...),
    job_description: str = Form(...),
    resume_file: UploadFile = File(...),
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
            db, current_user.id, job_title, job_description, resume_file
        )
    except Exception as e:
        logger.error(
            f"[MOCK_INTERVIEW_START] Failed to start interview for user {current_user.id}: {e}"
        )
        raise HTTPException(status_code=500, detail="Failed to start mock interview")


@router.post("/{session_id}/process", response_model=ProcessingStartedResponse)
async def process_interview(
    session_id: str,
    question_audio_map: str = Form(...),  # JSON mapping of question_id -> filenames
    audio_files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Processes all answers, evaluates them, and generates final interview results.
    """
    try:
        logger.info(
            f"[MOCK_PROCESS] Verifying access for user: {current_user.id}, session: {session_id}"
        )
        check_feature_access(db, current_user.id, FEATURE_MOCK_INTERVIEW)

        logger.info(
            f"[MOCK_PROCESS] Uploading audio files to S3 for session: {session_id}"
        )
        audio_file_map = await get_audio_file_map(
            current_user.id, session_id, audio_files
        )

        from app.utils.aws_utils import send_to_mock_interview_queue

        logger.info(f"[MOCK_PROCESS] Dispatching session: {session_id} to SQS queue")

        send_to_mock_interview_queue(
            {
                "user_id": current_user.id,
                "session_id": session_id,
                "question_audio_map": ast.literal_eval(question_audio_map),
                "audio_file_map": audio_file_map,
            }
        )

        logger.info(
            f"[MOCK_PROCESS] Mock interview session {session_id} queued successfully"
        )

        return {
            "status": "processing",
            "message": "Your interview is being evaluated. You'll be notified once it's done.",
        }
    except Exception as e:
        logger.error(f"[MOCK_PROCESS] Failed to process session {session_id}: {e}")
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
