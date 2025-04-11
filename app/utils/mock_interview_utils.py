import json
import logging

from sqlalchemy.orm import Session

from app.database.auth import get_user_by_id
from app.utils.aws_utils import generate_presigned_url
from app.utils.constants import EMAIL_SUB, EMAIL_BODY
from app.utils.email_utils import send_email
from app.utils.openai_client import call_openai
from app.utils.prompts import INTERVIEW_EVALUATION_PROMPT
from app.utils.utils import parse_ai_response, calculate_interview_duration

logger = logging.getLogger("app")
queue_logger = logging.getLogger("sqs")


def format_skipped_question(question):
    """Returns a default response for skipped questions."""
    logger.warning(f"⚠️ No audio found for question_id: {question['question_id']}")
    return {
        "question_id": question["question_id"],
        "question": question["question"],
        "audio_s3_url": "",
        "transcription": "",
        "score": 0.0,
        "feedback": "No response provided.",
        "follow_up_question": ""
    }

def get_openai_interview_evaluation(job_title: str, interview_log: list[dict[str, any]]):
    """Calls OpenAI once to evaluate all answers and provide interview-level assessment."""
    logger.info(f"📡 Calling OpenAI for interview evaluation for job: {job_title}")
    prompt = INTERVIEW_EVALUATION_PROMPT.format(
        job_title=job_title,
        interview_log=json.dumps(interview_log, indent=2)
    )
    response = call_openai(prompt)
    logger.info("✅ Received evaluation response from OpenAI")
    return response


def process_ai_response(ai_response_json: str, interview_log: list[dict[str, any]]):
    """Parses OpenAI response and maps it to evaluation results."""
    logger.info("🧠 Parsing AI interview evaluation response")
    ai_data = parse_ai_response(ai_response_json)

    evaluation_results = []
    for entry in interview_log:
        question_id = entry["question_id"]
        eval_data = ai_data["question_evaluations"].get(question_id, {})

        evaluation_results.append({
            "question_id": question_id,
            "question": entry["question"],
            "audio_presigned_url": generate_presigned_url(entry["audio_s3_url"]) if entry["audio_s3_url"] else "",
            "score": eval_data.get("score", 0.0),
            "feedback": eval_data.get("feedback", "No feedback available."),
            "follow_up_question": eval_data.get("follow_up_question", "")
        })

    final_evaluation = ai_data.get("final_assessment", {})
    logger.info("✅ Finished processing AI evaluation results")
    return evaluation_results, final_evaluation


async def send_interview_result_email(db: Session, user_id: str, session, final_evaluation):
    """Sends an email notification to the candidate with the interview results."""
    queue_logger.info(f"📧 Preparing to send interview result email for user: {user_id}")
    try:
        user = get_user_by_id(db, user_id)

        email_subject = EMAIL_SUB
        email_body = EMAIL_BODY.format(
            user_name=user.name,
            job_title=session.job_title,
            score=final_evaluation.get("overall_score", 0.0),
            strengths=", ".join(final_evaluation.get("key_strengths", [])),
            growth_areas=", ".join(final_evaluation.get("areas_for_growth", [])),
            duration=calculate_interview_duration(session.created_at),
            session_id=session.id,
        )

        await send_email(user.email, email_subject, email_body)
        logger.info(f"✅ Interview results email sent to user: {user.email}")
    except Exception as e:
        logger.error(
            f"❌ Failed to send interview results email to user {user_id}: {e}",
            exc_info=True,
        )
