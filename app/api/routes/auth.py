import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.auth import SyncUserRequest, SyncUserResponse
from app.services.auth_service import sync_user_service

router = APIRouter()

logger = logging.getLogger("app")

@router.post("/sync-user", response_model=SyncUserResponse)
async def sync_user(user_data: SyncUserRequest, db: Session = Depends(get_db)):
    """Syncs authenticated users into PostgreSQL using Google access token from request body."""
    logger.info("Received sync-user request.")
    if not user_data.access_token:
        logger.error("Access token missing in request body.")
        raise HTTPException(status_code=401, detail="Failed to login. Please try again.")

    # ✅ Sync user with the database
    try:
        user = sync_user_service(db, user_data.access_token)
        logger.info(f"User {user['user_id']} synced successfully with plan: {user['plan_code']}")
        return user
    except Exception as e:
        logger.error(f"Exception while syncing user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal error while syncing user.")
