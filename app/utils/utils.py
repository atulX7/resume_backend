import json
import logging
import re
from datetime import timezone, datetime

logger = logging.getLogger("app")


def generate_question_id(user_id: str, session_id: str, counter: int):
    question_id = f"{user_id[:8]}-{session_id[:8]}-{counter}"
    logger.info(f"🆔 Generated question ID: {question_id}")
    return question_id


def parse_ai_response(ai_response):
    """Parses AI response handling cases with Markdown formatting, JSON-as-string, or empty response."""
    try:
        if not ai_response or ai_response.strip() == "":
            logger.warning("Empty or null AI response received.")
            return {}

        clean_response = re.sub(r"```json|```", "", ai_response).strip()
        parsed_response = json.loads(clean_response)
        logger.info("Successfully parsed AI response.")
        return parsed_response

    except json.JSONDecodeError as e:
        logger.error(f"JSONDecodeError while parsing AI response: {str(e)}")
        logger.warning(f"Raw AI response that caused error: {ai_response}")
        return {}

    except ValueError as e:
        logger.error(f"ValueError while parsing AI response: {str(e)}")
        logger.warning(f"Raw AI response that caused error: {ai_response}")
        return {}


def calculate_interview_duration(start_time: datetime) -> float:
    """
    Converts a given timestamp to UTC if needed and calculates the duration from now.

    :param start_time: The interview start time (can be timezone-aware or naive).
    :return: Duration of the interview in minutes.
    """
    logger.info(f"Calculating interview duration from UTC timestamp: {start_time}")
    try:
        current_time = datetime.now(timezone.utc)
        duration_in_minutes = round((current_time - start_time).total_seconds() / 60, 2)

        logger.info(f"Interview duration: {duration_in_minutes} minutes")
        return duration_in_minutes
    except Exception as e:
        logger.error(f"Failed to calculate interview duration: {str(e)}")
        return 0.0


def get_file_extension_from_s3_key(s3_key):
    try:
        file_extension = s3_key.rsplit(".", 1)[-1]
        logger.info(
            f"[S3_FILE_EXT] Extracted file extension '{file_extension}' from key: {s3_key}"
        )
        return file_extension
    except Exception as e:
        logger.error(
            f"[S3_FILE_EXT] Failed to extract file extension from S3 key: {s3_key} | Error: {e}",
            exc_info=True,
        )
        raise
