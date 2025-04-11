import logging

from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.database.plan import increment_feature_usage

logger = logging.getLogger("app")


def check_feature_access(db: Session, user_id: int, feature_key: str):
    logger.info(f"🔍 Checking feature access: user_id={user_id}, feature_key={feature_key}")

    allowed = increment_feature_usage(db, user_id, feature_key)
    if not allowed:
        logger.warning(f"⛔ Usage limit reached: user_id={user_id}, feature={feature_key}")
        raise HTTPException(
            status_code=403,
            detail="Usage limit reached. Please contact us for queries."
        )
    logger.info(f"✅ Feature access valid: user_id={user_id}, feature={feature_key}")