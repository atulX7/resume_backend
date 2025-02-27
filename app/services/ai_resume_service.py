from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.services.resume_service import handle_resume_upload
from app.utils.ai_assistant import analyze_resume_with_ai
from app.utils.aws_utils import generate_presigned_url


def tailor_resume(db: Session, user_id: str, job_title: str, job_description: str, skills: str, user_resume: UploadFile):
    """Sends the uploaded resume file as an attachment to AI for analysis and improvement recommendations."""

    # ✅ Call AI assistant to analyze resume
    ai_response = analyze_resume_with_ai(job_title, job_description, skills, user_resume)

    # ✅ Upload the AI-analyzed resume to S3 (optional, for user downloads)
    # resume = handle_resume_upload(db, user_id, user_resume, job_title)
    # s3_url = resume.s3_url
    s3_url = "https://so-3645-test-bucket.s3.amazonaws.com/b7465672-73a5-4ce0-bd35-69c2297c363a/resume_02118e79-aa1e-4792-b5ca-6f6363ab0dd0.pdf"

    return {
        "resume_url": generate_presigned_url(s3_url),
        "review_suggestions": ai_response
    }