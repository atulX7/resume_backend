from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.database.plan import increment_feature_usage


def check_feature_access(db: Session, user_id: int, feature_key: str):
    allowed = increment_feature_usage(db, user_id, feature_key)
    if not allowed:
        print(f"Usage limit reached for '{feature_key}' for user: {user_id}.")
        raise HTTPException(
            status_code=403,
            message="Usage limit reached. Please upgrade your plan."
        )