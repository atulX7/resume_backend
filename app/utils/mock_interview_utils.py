import json

from sqlalchemy.orm import Session

from app.database.auth import get_user_by_id
from app.utils.aws_utils import generate_presigned_url
from app.utils.email_utils import send_email
from app.utils.openai_client import call_openai
from app.utils.prompts import INTERVIEW_EVALUATION_PROMPT
from app.utils.utils import parse_ai_response, calculate_interview_duration


def format_skipped_question(question):
    """Returns a default response for skipped questions."""
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
    prompt = INTERVIEW_EVALUATION_PROMPT.format(
        job_title=job_title,
        interview_log=json.dumps(interview_log, indent=2)
    )
    response = call_openai(prompt)
    return response


def process_ai_response(ai_response_json: str, interview_log: list[dict[str, any]]):
    """Parses OpenAI response and maps it to evaluation results."""
    ai_data = parse_ai_response(ai_response_json)

    evaluation_results = []
    for entry in interview_log:
        question_id = entry["question_id"]
        eval_data = ai_data["question_evaluations"].get(question_id, {})

        evaluation_results.append({
            "question_id": question_id,
            "question": entry["question"],
            "audio_presigned_url": generate_presigned_url(entry["audio_s3_url"]),
            "score": eval_data.get("score", 0.0),
            "feedback": eval_data.get("feedback", "No feedback available."),
            "follow_up_question": eval_data.get("follow_up_question", "")
        })

    final_evaluation = ai_data.get("final_assessment", {})
    return evaluation_results, final_evaluation


async def send_interview_result_email(db: Session, user_id: str, session, final_evaluation):
    """Sends an email notification to the candidate with the interview results."""
    user = get_user_by_id(db, user_id)

    email_subject = "📢 Your Mock Interview Results Are Available!"
    email_body = f"""
    Hi {user.name},

    Your mock interview session for **{session.job_title}** has been evaluated. 

    - 🏆 **Overall Score:** {final_evaluation.get("overall_score", 0.0)}/10
    - 📊 **Key Strengths:** {", ".join(final_evaluation.get("key_strengths", []))}
    - 📌 **Areas for Growth:** {", ".join(final_evaluation.get("areas_for_growth", []))}
    - ⏳ **Duration:** {calculate_interview_duration(session.created_at)} minutes

    You can view your results here: [View Results](http://yourfrontend.com/interview/{session.id})

    Regards,  
    Mock Interview AI Team
    """

    await send_email(user.email, email_subject, email_body)


def format_final_response(final_evaluation, evaluation_results):
    """Formats the API response with structured evaluation data."""
    return {
        'overall_score': final_evaluation.get("overall_score", 0.0),
        'duration_in_minutes': final_evaluation.get("duration_in_minutes", 0.0),
        'key_strengths': final_evaluation.get("key_strengths", []),
        'areas_for_growth': final_evaluation.get("areas_for_growth", []),
        'skill_assessment': final_evaluation.get("skill_assessment", {}),
        'evaluation_results': evaluation_results
    }

