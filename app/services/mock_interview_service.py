import json
from typing import List
from sqlalchemy.orm import Session
from fastapi import UploadFile

from app.models.mock_interview import MockInterviewSession
from app.utils.constants import MAX_QUESTIONS_PER_SESSION, INTRO_QUESTION
from app.utils.mock_interview_utils import format_skipped_question, get_openai_interview_evaluation, \
    process_ai_response, send_interview_result_email, format_final_response
from app.utils.openai_client import call_openai
from app.utils.prompts import INTERVIEW_QUESTION_PROMPT
from app.utils.aws_utils import upload_resume_to_s3, transcribe_audio, upload_audio_to_s3, \
    generate_presigned_url
from app.database.mock_interview import (
    create_mock_interview_session,
    get_mock_interview_session,
    update_mock_interview_session, save_interview_results
)

from app.utils.resume_parser import extract_resume_text
from app.utils.utils import generate_question_id, parse_ai_response


def start_mock_interview(db: Session, user_id: str, job_title: str, job_description: str, resume_file: UploadFile):
    """Starts a new mock interview session by storing resume and initializing the interview."""
    # ✅ Extract resume text from S3
    resume_text = extract_resume_text(resume_file)
    # ✅ Upload resume to S3
    resume_s3_url = "https://so-3645-test-bucket.s3.amazonaws.com/b7465672-73a5-4ce0-bd35-69c2297c363a/resume_02118e79-aa1e-4792-b5ca-6f6363ab0dd0.pdf"
    # resume_s3_url = upload_resume_to_s3(resume_file, user_id)

    # ✅ Create a new session
    session = create_mock_interview_session(db, user_id, job_title, job_description, resume_s3_url)

    # ✅ Generate remaining 19 questions in one API call
    prompt = INTERVIEW_QUESTION_PROMPT.format(
        max_questions=MAX_QUESTIONS_PER_SESSION,
        resume_text=resume_text,
        job_title=job_title,
        job_description=job_description,
    )
    # ai_response = call_openai(prompt)
#     ai_response = '''
#     {
#   "questions" : [ "Can you elaborate on a project where you had to migrate infrastructure to Google Cloud and how you ensured the transition was seamless?", "Describe a scenario where you worked collaboratively with a cross-functional team to obtain data-driven insights that drove business growth.", "How do you stay up-to-date with the latest trends and advancements in machine learning and data science?", "Have you had the opportunity to lead and mentor a team in the past? How did you ensure their professional growth and development?", "What strategies do you use to maintain and optimize machine learning models for accuracy and efficiency?", "Can you discuss a time when you had to solve a complex problem using machine learning? How did you approach it?", "How do you ensure that the technical solutions you build align with company strategy and adhere to industry standards?", "Can you describe your experience with end-to-end ML workflows, and how you ensure each step is efficient?", "Have you ever built and deployed machine learning models at scale? What were the key factors you considered?", "What programming languages and tools do you prefer for developing ML models, and why?", "How would you foster a continuous learning environment within a team or organization?", "Can you share an example where you had to adapt quickly to a new technology or tool in a project?", "How do you evaluate the success and performance of your machine learning projects or strategies?", "Describe a situation where you had to implement service observability and monitoring in a project. What tools or methodologies did you use?", "How would you go about building a strong team of ML/AI leaders to expand an organization’s footprint in the industry?", "Describe a time when you implemented a data science strategy that resulted in significant business impact.", "What role does cloud computing play in your work with machine learning, and how do you utilize it effectively?", "Can you discuss a challenging interpersonal issue you faced in a team setting and how you resolved it?", "How do you balance innovation with maintaining operational efficiency in machine learning projects?" ]
# }
#     '''
    ai_response = '''
        {
      "questions" : [ "Can you elaborate on a project where you had to migrate infrastructure to Google Cloud and how you ensured the transition was seamless?"]
    }
        '''
    try:
        generated_questions = parse_ai_response(ai_response)["questions"]
    except json.JSONDecodeError:
        return {"error": "Failed to parse AI response"}
    # ✅ Combine all questions
    all_questions = [INTRO_QUESTION] + generated_questions[:MAX_QUESTIONS_PER_SESSION]

    # ✅ Assign structured question IDs
    questions_with_ids = []
    for counter, question in enumerate(all_questions, start=1):
        question_id = generate_question_id(user_id, session.id, counter)  # Unique identifier
        questions_with_ids.append({"question_id": question_id, "question": question})

    # ✅ Store questions in session
    session.previous_questions = questions_with_ids
    update_mock_interview_session(db, session)

    return {
        'session_id':session.id,
        'questions':questions_with_ids
    }



async def process_mock_interview(db: Session, user_id: str, session_id: str, question_audio_map: dict[str, str], audio_files: List[UploadFile]):
    """Processes all answers, evaluates them, and generates final interview results."""
    session = get_mock_interview_session(db, session_id)
    if not session:
        raise Exception(f"Session {session_id} not found")

    filename_to_audio = {file.filename: file for file in audio_files}
    interview_log = []

    # ✅ Step 1: Process Transcriptions
    for question in session.previous_questions:
        question_id = question["question_id"]
        audio_filename = question_audio_map.get(question_id)

        if not audio_filename or audio_filename not in filename_to_audio:
            interview_log.append(format_skipped_question(question))
            continue

        audio_file = filename_to_audio[audio_filename]
        # audio_s3_url = upload_audio_to_s3(audio_file, user_id, session_id, question_id)
        audio_s3_url = 'https://so-3645-test-bucket.s3.amazonaws.com/b7465672-73a5-4ce0-bd35-69c2297c363a/mock_interviews/cd156fa5-e52f-4f02-83df-f2e4456735c5/audio_b7465672-cd156fa5-1.mp3'
        # transcription_text = transcribe_audio(audio_s3_url)
        transcription_text = "Scenario based questions in any technical interview are asked to assess the depth of your knowledge. So whenever you get a scenario based question, don't jump to the answer. Try to assess the situation. They are basically trying to differentiate you from other people. They are also trying to understand, do you really have production like uh experience in your resume. So they they want to throw a random scenario at you. Probably that has something happened in their area or that they have experienced themselves. They want to assess what options you will be performing, what activities you will be performing in such a scenario. So start before you start answering the question. Try to assess, try to understand what was the situation, what sort of services they use, what was the scenario. Get more details about the question, and then start framing your answer. That will help you score better in these kind of questions."

        interview_log.append({
            "question_id": question_id,
            "question": question["question"],
            "audio_s3_url": audio_s3_url,
            "transcription": transcription_text
        })

    # ✅ Step 2: Call OpenAI once for **all** questions
    # ai_response_json = get_openai_interview_evaluation(session.job_title, interview_log)
    ai_response_json = """
    {
    "question_evaluations": {
        "3102c45b-7252d078-1": {
            "score": 2,
            "feedback": "The candidate failed to provide an introduction or share any relevant career experiences, instead offering advice on how to approach scenario-based interview questions. This response did not fulfill the question’s request for personal career insights and achievements.",
            "follow_up_question": "Could you please share more about your career background and some key achievements you've had in your previous roles?"
        },
        "3102c45b-7252d078-2": {
            "score": 1,
            "feedback": "The candidate repeated the same response from the first question, failing to provide any details about a project involving the migration of infrastructure to Google Cloud. This lack of a specific answer did not demonstrate any relevant experience or knowledge of cloud migration, which was crucial for this question.",
            "follow_up_question": "Can you describe a specific project where you successfully migrated an infrastructure to the cloud, detailing the steps you took and the challenges you overcame?"
        }
    },
    "final_assessment": {
        "overall_score": 2,
        "key_strengths": [
         "The candidate attempted to discuss the importance of scenario-based questions, which indicates an understanding of the interview process and possibly a strategic approach to answering questions."
     ],
        "areas_for_growth": [
            "The candidate needs to provide direct answers that are specific to the questions asked.",
            "Improved structure and clarity in responses would be beneficial.",
            "Sharing personal experiences and achievements relevant to the role is crucial."
        ],
        "skill_assessment": {
            "technical": 1,
            "problem_solving": 2,
            "communication": 1,
            "leadership": 1,
            "adaptability": 1,
            "behavioral_fit": 1,
            "confidence": 2
        }
    }
}
    """

    # ✅ Step 3: Process AI response
    evaluation_results, final_evaluation = process_ai_response(ai_response_json, interview_log)

    # ✅ Step 4: Save interview evaluation in the database
    save_interview_results(db, session, evaluation_results, final_evaluation)

    # ✅ Step 5: Send email notification to user
    await send_interview_result_email(db, user_id, session, final_evaluation)

    return format_final_response(final_evaluation, evaluation_results)



def get_mock_interview_sessions_for_user(db: Session, user_id: str):
    """Fetches all mock interview sessions for a given user."""
    sessions = db.query(MockInterviewSession).filter(MockInterviewSession.user_id == user_id).all()

    return [
        {
            "session_id": session.id,
            "job_title": session.job_title,
            "created_at": session.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "status": session.status
        }
        for session in sessions
    ]


def get_mock_interview_session_details(db: Session, session_id: str):
    """Fetches detailed information about a specific mock interview session."""
    session = db.query(MockInterviewSession).filter(MockInterviewSession.id == session_id).first()

    if not session:
        raise Exception(f"Session {session_id} not found")

    evaluation_results = [
        {
            "question_id": entry.get("question_id"),
            "question": entry["question"],
            "audio_presigned_url": generate_presigned_url(entry["audio_s3_url"]) if entry.get("audio_s3_url") else "",
            "score": entry.get("score", 0.0),
            "feedback": entry.get("feedback", ""),
            "follow_up_question": entry.get("follow_up_question", "")
        }
        for entry in session.interview_log
    ]

    return {
        "session_id": session.id,
        "job_title": session.job_title,
        "created_at": session.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "status": session.status,
        "overall_score": session.ai_feedback.get("overall_score", 0.0) if session.ai_feedback else None,
        "key_strengths": session.ai_feedback.get("key_strengths", []) if session.ai_feedback else [],
        "areas_for_growth": session.ai_feedback.get("areas_for_growth", []) if session.ai_feedback else [],
        "skill_assessment": session.ai_feedback.get("skill_assessment", {}) if session.ai_feedback else {},
        "evaluation_results": evaluation_results
    }
