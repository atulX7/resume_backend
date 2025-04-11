import logging
from sqlalchemy.orm import Session

from app.schemas.share import ResumeShareRequest, ResumeShareResponse
from app.utils.aws_utils import generate_presigned_url
from app.database.resume import get_resume

logger = logging.getLogger("app")


def share_resume(db: Session, request: ResumeShareRequest):
    """Generates a public link for a resume."""
    logger.info(f"[RESUME_SHARE] Requested share link for resume ID: {request.resume_id}")

    try:
        resume = get_resume(db, request.resume_id)
        if not resume:
            logger.warning(f"[RESUME_SHARE] Resume not found for ID: {request.resume_id}")
            raise Exception("Resume not found")

        logger.info(f"[RESUME_SHARE] Generating presigned URL for resume ID: {request.resume_id}")
        public_url = generate_presigned_url(resume.s3_url)

        logger.info(f"[RESUME_SHARE] Successfully generated shareable URL for resume ID: {request.resume_id}")
        return ResumeShareResponse(public_url=public_url)

    except Exception as e:
        logger.error(f"[RESUME_SHARE] Failed to generate shareable link for resume ID: {request.resume_id}. Error: {str(e)}", exc_info=True)
        raise
