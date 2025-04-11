import json
import logging

from fastapi import UploadFile

from app.core.config import settings
from app.schemas.scoring import ResumeScoringResponse
from app.utils.mock_data import MOCK_SCORE
from app.utils.prompts import RESUME_SCORING_PROMPT
from app.utils.resume_parser import extract_resume_text
from app.utils.utils import parse_ai_response
from app.utils.openai_client import call_openai

logger = logging.getLogger("app")


def score_resume(resume_file: UploadFile):
    """Analyzes and scores a resume."""
    logger.info(f"[RESUME_SCORING] Starting resume scoring for uploaded file: {resume_file.filename}")
    try:
        if settings.MOCK_DATA:
            logger.info("[RESUME_SCORING] Using mock data for scoring.")
            ai_response = MOCK_SCORE
        else:
            resume_text = extract_resume_text(resume_file)
            logger.info("[RESUME_SCORING] Extracted resume text. Generating AI prompt.")
            prompt = RESUME_SCORING_PROMPT.format(resume_text=resume_text)
            logger.info("[RESUME_SCORING] Sending prompt to OpenAI for scoring.")
            ai_response = call_openai(prompt)

        try:
            scores = parse_ai_response(ai_response)  # Convert AI response to a dictionary
            logger.info("[RESUME_SCORING] Successfully parsed AI response.")
        except json.JSONDecodeError as e:
            logger.error(f"[RESUME_SCORING] Failed to decode AI response: {str(e)}", exc_info=True)
            scores = {}  # Default empty dict if parsing fails
        except Exception as e:
            logger.error(f"[RESUME_SCORING] Unexpected error while parsing AI response: {str(e)}", exc_info=True)
            scores = {}

        return ResumeScoringResponse(scores=scores)
    except Exception as e:
        logger.error(f"[RESUME_SCORING] Scoring failed for file {resume_file.filename}: {str(e)}", exc_info=True)
        raise