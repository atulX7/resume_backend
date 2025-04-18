import json
import uuid

from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException
import logging

from app.core.config import settings
from app.utils.constants import (
    MAX_QUESTIONS_PER_SESSION,
    INTRO_QUESTION,
    MOCK_INTERVIEW_PREV_Q_FILE,
    MOCK_INTERVIEW_PREV_JD_FILE,
    MOCK_INTERVIEW_AI_FEEDBACK_FILE,
    MOCK_INTERVIEW_LOG_FILE,
)
from app.utils.mock_data import (
    MOCK_INTERVIEW_QUESTIONS_RESPONSE,
    MOCK_RESUME_S3_URL,
    MOCK_JD_S3_URL,
    MOCK_PREV_QUESTIONS_S3_URL,
    MOCK_AUDIO_S3_URL,
    MOCK_AUDIO_TRANSCRIPTION_TEXT,
    MOCK_INTERVIEW_EVALUATION_RESPONSE,
    MOCK_RESUME_STORAGE_KEY,
    MOCK_JD_STORAGE_KEY,
    MOCK_QUES_MAP_STORAGE_KEY,
)
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
    load_json_from_s3,
    send_to_mock_interview_queue,
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
    logger.info(
        f"[MOCK START] Starting interview for user: {user_id}, job: {job_title}, session: {session_id}"
    )
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
        all_questions = [INTRO_QUESTION] + generated_questions[
            :MAX_QUESTIONS_PER_SESSION
        ]

        questions_with_ids = []
        for counter, question in enumerate(all_questions, start=1):
            question_id = generate_question_id(user_id, session_id, counter)
            questions_with_ids.append(
                {"question_id": question_id, "question": question, "answer_audio": ""}
            )

        if settings.MOCK_DATA:
            resume_storage_key = MOCK_RESUME_STORAGE_KEY
            jd_storage_key = MOCK_JD_STORAGE_KEY
            question_map_storage_key = MOCK_QUES_MAP_STORAGE_KEY
        else:
            question_map_storage_key = upload_mock_interview_data(
                user_id, session_id, MOCK_INTERVIEW_PREV_Q_FILE, questions_with_ids
            )
            resume_storage_key = upload_resume_to_s3(resume_file, user_id, session_id)
            jd_json = {"jd": job_description}
            jd_storage_key = upload_mock_interview_data(
                user_id, session_id, MOCK_INTERVIEW_PREV_JD_FILE, jd_json
            )

        create_mock_interview_session(
            db,
            session_id,
            user_id,
            job_title,
            jd_storage_key,
            resume_storage_key,
            question_map_storage_key,
        )
        logger.info(f"✅ Mock interview session created: {session_id}")
        return {"session_id": session_id, "questions": questions_with_ids}

    except Exception as e:
        logger.error(
            f"❌ Failed to start mock interview for user: {user_id}, Error: {str(e)}"
        )
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
        logger.error(
            f"❌ Error uploading audio files for session: {session_id}, Error: {str(e)}"
        )
        raise


async def process_mock_interview_worker(
    db: Session,
    user_id: str,
    session_id: str,
):
    """Processes all answers, evaluates them, and generates final interview results."""
    session_status = "failed"
    interview_log_storage_key = ""
    ai_feedback_storage_key = ""
    try:
        queue_logger.info(
            f"[JOB] Starting interview processing for user: {user_id}, session: {session_id}"
        )
        session = get_mock_interview_session(db, session_id)
        if not session:
            queue_logger.warning(f"[JOB] Session {session_id} not found")
            return

        interview_log = []
        # Load questions mapping from storage (which now includes answer_audio file keys)
        mapping_from_storage = load_json_from_s3(session.questions_mapping_storage_key)
        if not mapping_from_storage:
            queue_logger.error(
                f"[JOB] Questions mapping file missing for session {session_id}"
            )
            return

        # Iterate over each question and process the answer
        for question in mapping_from_storage:
            question_id = question.get("question_id")
            answer_audio_key = question.get("answer_audio")
            queue_logger.info(
                f"[JOB] Processing question id: {question_id}, answer_audio_key: {answer_audio_key}"
            )

            if not answer_audio_key:
                queue_logger.warning(
                    f"[JOB] Missing answer audio for question: {question_id}"
                )
                interview_log.append(format_skipped_question(question))
                continue

            if settings.MOCK_DATA:
                queue_logger.info("Returning mock data")
                transcription_text = MOCK_AUDIO_TRANSCRIPTION_TEXT
            else:
                queue_logger.info(f"Transcribing audio: {answer_audio_key}")
                transcription_text = transcribe_audio(answer_audio_key)

            interview_log.append(
                {
                    "question_id": question_id,
                    "question": question["question"],
                    "audio_storage_key": answer_audio_key,
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
        queue_logger.info("[JOB] Processed AI evaluation response.")

        # Re-upload evaluation results and AI feedback as JSON to storage.
        interview_log_storage_key = upload_mock_interview_data(
            user_id, session_id, MOCK_INTERVIEW_LOG_FILE, evaluation_results
        )
        ai_feedback_storage_key = upload_mock_interview_data(
            user_id, session_id, MOCK_INTERVIEW_AI_FEEDBACK_FILE, final_evaluation
        )
        session_status = "completed"
        queue_logger.info(
            f"[JOB] Updated interview evaluation data for session {session_id}"
        )

        # Send the final results via email (asynchronously).
        await send_interview_result_email(db, user_id, session, final_evaluation)
        queue_logger.info(f"[JOB] Finished processing session {session_id}")
    except Exception as e:
        queue_logger.error(
            f"[JOB] Error processing session {session_id}: {e}", exc_info=True
        )
    finally:
        # Save the final processing state in the database.
        save_interview_results(
            db,
            session,
            interview_log_storage_key,
            ai_feedback_storage_key,
            session_status,
        )


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

    interview_log = load_json_from_s3(session.interview_log_storage_key)
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

    ai_feedback = load_json_from_s3(session.ai_feedback_storage_key)
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


async def update_question_mapping_for_answer(
    db: Session,
    session_id: str,
    user_id: str,
    question_id: str,
    answer_audio,  # This is an UploadFile instance
) -> dict:
    """
    Uploads the candidate's answer audio file and updates the S3-stored questions mapping file
    to insert the new answer_audio file key for the corresponding question.
    """
    # --- Step 1. Upload the audio file ---
    try:
        content = await answer_audio.read()
        storage_file_key = await upload_audio_to_s3_async(
            content,
            user_id,
            session_id,
            answer_audio.filename,
            answer_audio.content_type,
        )
        logger.info(
            f"[SERVICE] Uploaded answer audio for question {question_id}; received file key: {storage_file_key}"
        )
    except Exception as exc:
        logger.error(
            f"[SERVICE] Error during S3 upload for question {question_id}: {exc}",
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Audio upload failed") from exc

    # --- Step 2. Retrieve the session and load the questions mapping file ---
    session_obj = get_mock_interview_session(db, session_id)
    try:
        questions_mapping = load_json_from_s3(session_obj.questions_mapping_storage_key)
        logger.info(
            f"[SERVICE] Fetched questions mapping file for session {session_id}"
        )
    except Exception as exc:
        logger.error(
            f"[SERVICE] Error fetching questions mapping for session {session_id}: {exc}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500, detail="Failed to fetch questions mapping"
        ) from exc

    # --- Step 3. Update the question mapping ---
    updated = False
    for item in questions_mapping:
        if item.get("question_id") == question_id:
            item["answer_audio"] = storage_file_key
            updated = True
            logger.info(
                f"[SERVICE] Updated question {question_id} with new answer audio file key."
            )
            break

    if not updated:
        logger.error(
            f"[SERVICE] Question ID {question_id} not found in mapping file for session {session_id}"
        )
        raise HTTPException(status_code=400, detail="Question ID not found in mapping")

    # --- Step 4. Re-upload the updated questions mapping file ---
    try:
        new_prev_q_key = upload_mock_interview_data(
            user_id, session_id, MOCK_INTERVIEW_PREV_Q_FILE, questions_mapping
        )
        logger.info(
            f"[SERVICE] Re-uploaded questions mapping file for session {session_id}; new file key: {new_prev_q_key}"
        )
        # Update the session record (if needed)
        session_obj.questions_mapping_storage_key = new_prev_q_key
        db.commit()
        db.refresh(session_obj)
    except Exception as exc:
        logger.error(
            f"[SERVICE] Failed to update questions mapping file for session {session_id}: {exc}",
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Failed to update questions mapping")

    return {"status": "success", "answer_audio_key": storage_file_key}
