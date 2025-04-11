import logging

from app.utils.openai_client import call_openai
from app.utils.prompts import JD_TAILORING_PROMPT
from app.utils.resume_parser import extract_resume_text

logger = logging.getLogger("app")

def analyze_resume_with_ai(
    job_title: str, job_description: str, skills: str, resume_file
):
    """Sends resume as an attachment to AI and retrieves structured review suggestions."""
    logger.info(f"[RESUME_ANALYSIS] Analyzing resume for job: '{job_title}'")
    try:
        resume_content = extract_resume_text(resume_file)
        logger.info("[RESUME_ANALYSIS] Resume content successfully extracted")

        prompt = JD_TAILORING_PROMPT.format(
            job_description=job_description,
            job_title=job_title,
            resume_content=resume_content,
            skills=skills,
        )

        logger.info("[RESUME_ANALYSIS] Sending data to OpenAI for tailoring response")
        content = call_openai(prompt)

        logger.info("[RESUME_ANALYSIS] Successfully received response from OpenAI")
        return content

    except Exception as e:
        logger.error(f"[RESUME_ANALYSIS] Error during resume analysis for job: '{job_title}'. Error: {str(e)}",
                     exc_info=True)
        raise
