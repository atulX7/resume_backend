from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.auth import SyncUserRequest, SyncUserResponse
from app.services.auth_service import sync_user_service

router = APIRouter()


@router.post("/sync-user", response_model=SyncUserResponse)
async def sync_user(user_data: SyncUserRequest, db: Session = Depends(get_db)):
    """Syncs authenticated users into PostgreSQL using Google access token from request body."""

    if not user_data.access_token:
        raise HTTPException(status_code=401, detail="Access token is required")

    # ✅ Sync user with the database
    user = sync_user_service(db, user_data.access_token)

    return user
