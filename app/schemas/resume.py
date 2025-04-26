from pydantic import BaseModel
from typing import Dict


class ResumeResponse(BaseModel):
    id: str
    user_id: str
    title: str
    s3_url: str
    resume_data: Dict


class TmpUploadResponse(BaseModel):
    temp_key: str
