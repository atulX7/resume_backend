from pydantic import BaseModel
from typing import Optional

class CoverLetterRequest(BaseModel):
    user_id: str
    job_title: str
    company_name: str
    job_description: Optional[str] = None  # Optional detailed JD
    user_resume: Optional[str] = None  # Optional existing resume

class CoverLetterResponse(BaseModel):
    generated_cover_letter: str
