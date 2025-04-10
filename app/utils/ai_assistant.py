from app.utils.openai_client import call_openai
from app.utils.prompts import JD_TAILORING_PROMPT
from app.utils.resume_parser import extract_resume_text


def analyze_resume_with_ai(
    job_title: str, job_description: str, skills: str, resume_file
):
    """Sends resume as an attachment to AI and retrieves structured review suggestions."""
    resume_content = extract_resume_text(resume_file)
    prompt = JD_TAILORING_PROMPT.format(
        job_description=job_description,
        job_title=job_title,
        resume_content=resume_content,
        skills=skills,
    )
    content = call_openai(prompt)
    return content
