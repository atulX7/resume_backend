from pydantic import BaseModel

class ResumeShareRequest(BaseModel):
    user_id: str
    resume_id: str

class ResumeShareResponse(BaseModel):
    public_url: str
