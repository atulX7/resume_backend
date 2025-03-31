import json

from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.middleware.auth_dependency import get_current_user
from app.services.mock_interview_service import (
    start_mock_interview, process_mock_interview, get_mock_interview_sessions_for_user,
    get_mock_interview_session_details
)
from app.schemas.mock_interview import (
    MockInterviewQuestionResponse, MockInterviewSessionSummary,
    MockInterviewSessionDetails, ProcessingStartedResponse
)
from app.utils.constants import FEATURE_MOCK_INTERVIEW
from app.utils.plan_usage import check_feature_access

router = APIRouter()

@router.post("/start", response_model=MockInterviewQuestionResponse)
async def start_interview(
    job_title: str = Form(...),
    job_description: str = Form(...),
    resume_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Starts a mock interview session and generates all questions in one call."""
    check_feature_access(db, current_user.id, FEATURE_MOCK_INTERVIEW)
    return start_mock_interview(db, current_user.id, job_title, job_description, resume_file)


@router.post("/{session_id}/process", response_model=ProcessingStartedResponse)
async def process_interview(
    session_id: str,
    question_audio_map: str = Form(...),  # JSON mapping of question_id -> filenames
    audio_files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Processes all answers, evaluates them, and generates final interview results.
    """
    check_feature_access(db, current_user.id, FEATURE_MOCK_INTERVIEW)
    # question_audio_map = json.loads(question_audio_map)  # Convert JSON string to dict
    # Schedule background processing
    # Convert the uploaded files into a list of dictionaries (read into memory)
    audio_file_data = []
    for file in audio_files:
        content = await file.read()
        audio_file_data.append({
            "filename": file.filename,
            "content": content,
            "content_type": file.content_type,
        })

    # Instead of calling process_mock_interview directly, queue the task.
    # We pass question_audio_map as-is (a JSON string) so it is serializable.
    from app.tasks.mock_interview import process_mock_interview_task  # import here to avoid circular imports
    process_mock_interview_task.delay(
        current_user.id,
        session_id,
        question_audio_map,  # already a JSON string from the form
        audio_file_data
    )

    return {
        "status": "processing",
        "message": "Your interview is being evaluated. You'll be notified once it's done."
    }


@router.get("/sessions", response_model=list[MockInterviewSessionSummary])
async def get_user_mock_interview_sessions(
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """
    Retrieves a list of all mock interview sessions for a given user.
    """
    return get_mock_interview_sessions_for_user(db, current_user.id)


@router.get("/sessions/{session_id}", response_model=MockInterviewSessionDetails)
async def get_mock_interview_details(
        session_id: str,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """
    Retrieves detailed information about a specific mock interview session.
    """
    return get_mock_interview_session_details(db, session_id)
