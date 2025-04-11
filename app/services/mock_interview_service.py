import json
import uuid

from sqlalchemy.orm import Session
from fastapi import UploadFile
import logging

from app.core.config import settings
from app.utils.constants import MAX_QUESTIONS_PER_SESSION, INTRO_QUESTION, MOCK_INTERVIEW_PREV_Q_FILE, \
    MOCK_INTERVIEW_PREV_JD_FILE, MOCK_INTERVIEW_AI_FEEDBACK_FILE, MOCK_INTERVIEW_LOG_FILE
from app.utils.mock_data import MOCK_INTERVIEW_QUESTIONS_RESPONSE, MOCK_RESUME_S3_URL, MOCK_JD_S3_URL, \
    MOCK_PREV_QUESTIONS_S3_URL, MOCK_AUDIO_S3_URL, MOCK_AUDIO_TRANSCRIPTION_TEXT, MOCK_INTERVIEW_EVALUATION_RESPONSE
from app.utils.mock_interview_utils import (
    format_skipped_question,
    get_openai_interview_evaluation,
    process_ai_response,
    send_interview_result_email,
)
from app.utils.openai_client import call_openai
from app.utils.prompts import INTERVIEW_QUESTION_PROMPT
from app.utils.aws_utils import (
    upload_resume_to_s3,
    transcribe_audio,
    upload_audio_to_s3_sync,
    generate_presigned_url,
    upload_mock_interview_data,
    fetch_mock_interview_data,
)
from app.database.mock_interview import (
    create_mock_interview_session,
    get_mock_interview_session,
    save_interview_results,
    get_mock_interview_sessions_by_user,
)

from app.utils.resume_parser import extract_resume_text
from app.utils.utils import generate_question_id, parse_ai_response
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=10)  # Match max_concurrency

queue_logger = logging.getLogger("sqs")  # This logger writes to logs/sqs.log
logger = logging.getLogger("app")


async def upload_audio_to_s3_async(*args, **kwargs):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        executor, upload_audio_to_s3_sync, *args, **kwargs
    )


def start_mock_interview(
    db: Session,
    user_id: str,
    job_title: str,
    job_description: str,
    resume_file: UploadFile,
):
    """Starts a new mock interview session by storing resume and initializing the interview."""
    session_id = str(uuid.uuid4())
    logger.info(f"[MOCK START] Starting interview for user: {user_id}, job: {job_title}, session: {session_id}")
    try:
        if settings.MOCK_DATA:
            logger.info("Using mock data for questions.")
            ai_response = MOCK_INTERVIEW_QUESTIONS_RESPONSE
        else:
            resume_text = extract_resume_text(resume_file)
            prompt = INTERVIEW_QUESTION_PROMPT.format(
                max_questions=MAX_QUESTIONS_PER_SESSION,
                resume_text=resume_text,
                job_title=job_title,
                job_description=job_description,
            )
            ai_response = call_openai(prompt)

        generated_questions = parse_ai_response(ai_response)["questions"]
        all_questions = [INTRO_QUESTION] + generated_questions[:MAX_QUESTIONS_PER_SESSION]

        questions_with_ids = []
        for counter, question in enumerate(all_questions, start=1):
            question_id = generate_question_id(user_id, session_id, counter)
            questions_with_ids.append({"question_id": question_id, "question": question})

        if settings.MOCK_DATA:
            resume_s3_url = MOCK_RESUME_S3_URL
            jd_s3_url = MOCK_JD_S3_URL
            prev_question_s3_url = MOCK_PREV_QUESTIONS_S3_URL
        else:
            prev_question_s3_url = upload_mock_interview_data(user_id, session_id, MOCK_INTERVIEW_PREV_Q_FILE,
                                                              questions_with_ids)
            resume_s3_url = upload_resume_to_s3(resume_file, user_id, session_id)
            jd_json = {"jd": job_description}
            jd_s3_url = upload_mock_interview_data(user_id, session_id, MOCK_INTERVIEW_PREV_JD_FILE, jd_json)

        create_mock_interview_session(db, session_id, user_id, job_title, jd_s3_url, resume_s3_url,
                                      prev_question_s3_url)
        logger.info(f"✅ Mock interview session created: {session_id}")
        return {"session_id": session_id, "questions": questions_with_ids}

    except Exception as e:
        logger.error(f"❌ Failed to start mock interview for user: {user_id}, Error: {str(e)}")
        raise


async def get_audio_file_map(user_id, session_id, audio_files):
    try:
        if settings.MOCK_DATA:
            return {file.filename: MOCK_AUDIO_S3_URL for file in audio_files}

        upload_tasks = []
        for file in audio_files:
            content = await file.read()
            upload_tasks.append(
                upload_audio_to_s3_async(
                    content, user_id, session_id, file.filename, file.content_type
                )
            )
        audio_s3_urls = await asyncio.gather(*upload_tasks)
        return {file.filename: url for file, url in zip(audio_files, audio_s3_urls)}
    except Exception as e:
        logger.error(f"❌ Error uploading audio files for session: {session_id}, Error: {str(e)}")
        raise


async def process_mock_interview(
    db: Session,
    user_id: str,
    session_id: str,
    question_audio_map: dict[str, str],
    audio_file_map: dict,
):
    """Processes all answers, evaluates them, and generates final interview results."""
    session_status = "failed"
    interview_log_s3_url = ""
    ai_feedback_s3_url = ""
    try:
        queue_logger.info(f"[PROCESS START] user: {user_id}, session: {session_id}")
        session = get_mock_interview_session(db, session_id)
        if not session:
            queue_logger.warning(f"❌ Session {session_id} not found")
            return

        interview_log = []
        previous_questions = fetch_mock_interview_data(
            session.previous_questions_s3_url
        )
        for question in previous_questions:
            question_id = question["question_id"]
            audio_filename = question_audio_map.get(question_id)
            queue_logger.info(
                f"Processing question id: {question_id} having audio filename: {audio_filename}"
            )

            if not audio_filename or audio_filename not in audio_file_map:
                queue_logger.warning(f"⚠️ Missing audio for question: {question_id}")
                interview_log.append(format_skipped_question(question))
                continue

            audio_s3_url = audio_file_map[audio_filename]
            queue_logger.info(f"Got audio url: {audio_s3_url}")
            if settings.MOCK_DATA:
                queue_logger.info("Returning mock data")
                transcription_text = MOCK_AUDIO_TRANSCRIPTION_TEXT
            else:
                queue_logger.info(f"Transcribing audio: {audio_s3_url}")
                transcription_text = transcribe_audio(audio_s3_url)

            interview_log.append(
                {
                    "question_id": question_id,
                    "question": question["question"],
                    "audio_s3_url": audio_s3_url,
                    "transcription": transcription_text,
                }
            )

        if settings.MOCK_DATA:
            ai_response_json = MOCK_INTERVIEW_EVALUATION_RESPONSE
        else:
            # ✅ Step 2: Call OpenAI once for **all** questions
            ai_response_json = get_openai_interview_evaluation(
                session.job_title, interview_log
            )

        # ✅ Step 3: Process AI response
        evaluation_results, final_evaluation = process_ai_response(
            ai_response_json, interview_log
        )

        # ✅ Step 4: update interview evaluation data
        session_status = "completed"
        interview_log_s3_url = upload_mock_interview_data(
            user_id, session.id, MOCK_INTERVIEW_LOG_FILE, evaluation_results
        )
        ai_feedback_s3_url = upload_mock_interview_data(
            user_id, session.id, MOCK_INTERVIEW_AI_FEEDBACK_FILE, final_evaluation
        )

        # ✅ Step 5: Send email notification to user
        await send_interview_result_email(db, user_id, session, final_evaluation)
        queue_logger.info(f"✅ Finished processing session: {session_id}")
    except Exception as e:
        queue_logger.info(
            f"❌ Error processing mock interview session {session_id}: {str(e)}"
        )
    save_interview_results(db, session, interview_log_s3_url, ai_feedback_s3_url, session_status)


def get_mock_interview_sessions_for_user(db: Session, user_id: str):
    """Fetches all mock interview sessions for a given user."""
    logger.info(f"📥 Fetching all sessions for user: {user_id}")
    sessions = get_mock_interview_sessions_by_user(db, user_id)

    return [
        {
            "session_id": session.id,
            "job_title": session.job_title,
            "created_at": session.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "status": session.status,
        }
        for session in sessions
    ]


def get_mock_interview_session_details(db: Session, session_id: str):
    """Fetches detailed information about a specific mock interview session."""
    logger.info(f"📥 Fetching session details for session: {session_id}")
    session = get_mock_interview_session(db, session_id)
    if not session:
        logger.error(f"❌ Session {session_id} not found")
        raise Exception(f"Session {session_id} not found")

    interview_log = fetch_mock_interview_data(session.interview_log_s3_url)
    evaluation_results = [
        {
            "question_id": entry.get("question_id"),
            "question": entry["question"],
            "audio_presigned_url": generate_presigned_url(entry["audio_s3_url"])
            if entry.get("audio_s3_url")
            else "",
            "score": entry.get("score", 0.0),
            "feedback": entry.get("feedback", ""),
            "follow_up_question": entry.get("follow_up_question", ""),
        }
        for entry in interview_log
    ]

    ai_feedback = fetch_mock_interview_data(session.ai_feedback_s3_url)
    return {
        "session_id": session.id,
        "job_title": session.job_title,
        "created_at": session.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "status": session.status,
        "overall_score": ai_feedback.get("overall_score", 0.0) if ai_feedback else None,
        "key_strengths": ai_feedback.get("key_strengths", []) if ai_feedback else [],
        "areas_for_growth": ai_feedback.get("areas_for_growth", []) if ai_feedback else [],
        "skill_assessment": ai_feedback.get("skill_assessment", {}) if ai_feedback else {},
        "evaluation_results": evaluation_results
    }
