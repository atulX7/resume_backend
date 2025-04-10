import json
import re
from datetime import timezone, datetime


def generate_question_id(user_id: str, session_id: str, counter: int):
    return f"{user_id[:8]}-{session_id[:8]}-{counter}"


def parse_ai_response(ai_response):
    """Parses AI response handling cases with Markdown formatting, JSON-as-string, or empty response."""
    try:
        # ✅ Ensure AI response is not empty or null
        if not ai_response or ai_response.strip() == "":
            return {}

        # ✅ Remove Markdown-like formatting (```json ... ```)
        clean_response = re.sub(r"```json|```", "", ai_response).strip()
        parsed_response = json.loads(clean_response)
        return parsed_response

    except json.JSONDecodeError as e:
        print(f"⚠️ JSONDecodeError: {str(e)}. AI response was:\n{ai_response}")

    except ValueError as e:
        print(f"⚠️ ValueError: {str(e)}. AI response was:\n{ai_response}")


def calculate_interview_duration(start_time: datetime) -> float:
    """
    Converts a given timestamp to UTC if needed and calculates the duration from now.

    :param start_time: The interview start time (can be timezone-aware or naive).
    :return: Duration of the interview in minutes.
    """
    if start_time.tzinfo is None:
        # ✅ If tzinfo is None, assume it's UTC but store properly
        start_time = start_time.replace(tzinfo=timezone.utc)
    elif start_time.tzinfo != timezone.utc:
        # ✅ Convert non-UTC timezones to UTC
        start_time = start_time.astimezone(timezone.utc)

    # ✅ Get the current time in UTC
    current_time = datetime.now(timezone.utc)

    # ✅ Compute the duration in minutes
    duration_in_minutes = round((current_time - start_time).total_seconds() / 60, 2)

    return duration_in_minutes
