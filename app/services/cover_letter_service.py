COVER_LETTER_PROMPT = """
You are a professional career consultant. Generate a formal, well-structured cover letter for the following job:

Job Title: {job_title}
Company: {company_name}

Job Description:
{job_description}

Candidate Resume:
{user_resume}

Ensure the cover letter is personalized, engaging, and aligned with the job description.
"""

from sqlalchemy.orm import Session
from app.schemas.cover_letter import CoverLetterRequest, CoverLetterResponse


def generate_cover_letter(db: Session, request: CoverLetterRequest):
    """Generates an AI-powered cover letter."""
    prompt = COVER_LETTER_PROMPT.format(
        job_title=request.job_title,
        company_name=request.company_name,
        job_description=request.job_description or "No detailed JD provided.",
        user_resume=request.user_resume or "No resume provided."
    )

    generated_cover_letter = call_openai({"prompt": prompt})

    return CoverLetterResponse(generated_cover_letter=generated_cover_letter)
