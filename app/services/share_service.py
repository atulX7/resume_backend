from sqlalchemy.orm import Session
from app.schemas.share import ResumeShareRequest, ResumeShareResponse
from app.utils.aws_utils import generate_presigned_url
from app.database.resume import get_resume


def share_resume(db: Session, request: ResumeShareRequest):
    """Generates a public link for a resume."""
    resume = get_resume(db, request.resume_id)
    if not resume:
        raise Exception("Resume not found")

    public_url = generate_presigned_url(resume.s3_url)

    return ResumeShareResponse(public_url=public_url)
