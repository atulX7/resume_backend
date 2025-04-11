import logging
from datetime import datetime, timezone, timedelta

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
import requests

from app.database.auth import get_user_by_email
from app.database.connection import get_db
from app.utils.constants import GOOGLE_TOKEN_INFO_URL

logger = logging.getLogger("app")


def get_current_user(request: Request, db: Session = Depends(get_db)):
    """Validates the access token from NextAuth and retrieves the authenticated user."""
    auth_token = request.headers.get("authorization")

    if not auth_token or not auth_token.startswith("Bearer "):
        logger.warning("[AUTH] Missing or invalid authorization header")
        raise HTTPException(
            status_code=401, detail="Authentication token missing or invalid"
        )

    access_token = auth_token.split("Bearer ")[1]

    try:
        logger.info("[AUTH] Validating access token with Google...")
        google_response = requests.get(
            GOOGLE_TOKEN_INFO_URL, params={"access_token": access_token}
        )

        if google_response.status_code != 200:
            logger.warning("[AUTH] Google token validation failed")
            raise HTTPException(status_code=403, detail="Invalid token")

        google_user_data = google_response.json()
        user_email = google_user_data.get("email")
        logger.info(f"[AUTH] Google token valid. Email: {user_email}")

        # ✅ Fetch user from PostgreSQL using email
        user = get_user_by_email(db, user_email)
        if not user:
            logger.warning(f"[AUTH] No user found with email: {user_email}")
            raise HTTPException(status_code=404, detail="User not found")

        # ✅ Check if login is older than 24 hours
        if user.last_login_at:
            time_diff = datetime.now(timezone.utc) - user.last_login_at
            if time_diff > timedelta(hours=24):
                logger.warning(f"[AUTH] Session expired for user: {user.id}")
                raise HTTPException(
                    status_code=401, detail="Session expired. Please log in again."
                )
            else:
                logger.info(f"[AUTH] User {user.id} session is still valid")

        logger.info(f"[AUTH] Authenticated user: {user.id}")
        return user

    except Exception as e:
        logger.error(f"[AUTH] Failed to get current user: {str(e)}", exc_info=True)
        raise HTTPException(status_code=401, detail="Token validation failed")
