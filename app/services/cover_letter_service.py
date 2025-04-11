import logging

from app.utils.openai_client import call_openai
from sqlalchemy.orm import Session
from app.schemas.cover_letter import CoverLetterRequest, CoverLetterResponse
from app.utils.prompts import COVER_LETTER_PROMPT

logger = logging.getLogger("app")


def generate_cover_letter(db: Session, request: CoverLetterRequest):
    """Generates an AI-powered cover letter."""
    logger.info(
        f"[COVER_LETTER] Generating cover letter for job: {request.job_title} at company: {request.company_name}")

    try:
        prompt = COVER_LETTER_PROMPT.format(
            job_title=request.job_title,
            company_name=request.company_name,
            job_description=request.job_description or "No detailed JD provided.",
            user_resume=request.user_resume or "No resume provided.",
        )

        logger.info("[COVER_LETTER] Calling OpenAI API with generated prompt.")
        generated_cover_letter = call_openai({"prompt": prompt})
        logger.info("[COVER_LETTER] Successfully generated cover letter.")

        return CoverLetterResponse(generated_cover_letter=generated_cover_letter)

    except Exception as e:
        logger.exception(f"[COVER_LETTER] Failed to generate cover letter: {str(e)}")
        raise
