import json
import logging

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.utils.ai_assistant import analyze_resume_with_ai
from app.utils.mock_data import MOCK_TAILOR_RESPONSE
from app.utils.utils import parse_ai_response

logger = logging.getLogger("app")


def tailor_resume(
    db: Session,
    user_id: str,
    job_title: str,
    job_description: str,
    skills: str,
    user_resume: UploadFile,
):
    """Sends the uploaded resume file as an attachment to AI for analysis and improvement recommendations."""
    logger.info(
        f"[TAILOR_RESUME] Start tailoring resume for user: {user_id}, job: {job_title}"
    )

    if settings.MOCK_DATA:
        logger.info("[TAILOR_RESUME] Using MOCK data for resume tailoring.")
        ai_response = MOCK_TAILOR_RESPONSE
    else:
        logger.info("[TAILOR_RESUME] Calling AI assistant to analyze resume...")
        ai_response = analyze_resume_with_ai(
            job_title, job_description, skills, user_resume
        )

    try:
        review_suggestions = parse_ai_response(ai_response)
        logger.info("[TAILOR_RESUME] AI response parsed successfully.")
    except json.JSONDecodeError as e:
        logger.error(
            f"[TAILOR_RESUME] JSON decode error while parsing AI response: {str(e)}",
            exc_info=True,
        )
        review_suggestions = {}
    except Exception as e:
        logger.error(
            f"[TAILOR_RESUME] Unexpected error in tailoring: {str(e)}",
            exc_info=True,
        )
        review_suggestions = {}

    # try:
    #     logger.info("[TAILOR_RESUME] Uploading tailored resume to S3")
    #     resume = handle_resume_upload(db, user_id, user_resume, job_title)
    #     s3_url = generate_presigned_url(resume.s3_url)
    # except Exception as e:
    #     logger.error(
    #         f"[TAILOR_RESUME] Failed to upload tailored resume to S3: {str(e)}",
    #         exc_info=True,
    #     )
    #     s3_url = ""

    logger.info(f"[TAILOR_RESUME] Tailoring complete for user: {user_id}")
    return {"review_suggestions": review_suggestions}
