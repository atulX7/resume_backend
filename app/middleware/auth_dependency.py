from datetime import datetime, timezone, timedelta

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
import requests

from app.database.auth import get_user_by_email
from app.database.connection import get_db
from app.utils.constants import GOOGLE_TOKEN_INFO_URL


def get_current_user(request: Request, db: Session = Depends(get_db)):
    """Validates the access token from NextAuth and retrieves the authenticated user."""
    auth_token = request.headers.get("authorization")
    if not auth_token or not auth_token.startswith("Bearer "):
        raise HTTPException(
            status_code=401, detail="Authentication token missing or invalid"
        )

    access_token = auth_token.split("Bearer ")[1]

    try:
        # ✅ Validate access token with Google OAuth endpoint
        google_response = requests.get(
            GOOGLE_TOKEN_INFO_URL, params={"access_token": access_token}
        )

        if google_response.status_code != 200:
            raise HTTPException(status_code=403, detail="Invalid token")

        google_user_data = google_response.json()

        # ✅ Fetch user from PostgreSQL using email
        user = get_user_by_email(db, google_user_data["email"])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # ✅ Check if login is older than 24 hours
        if user.last_login_at and (datetime.now(timezone.utc) - user.last_login_at) > timedelta(hours=24):
            raise HTTPException(status_code=401, detail="Session expired. Please log in again.")

        return user
    except Exception as e:
        print(f"Failed to get current user: {str(e)}")
        raise HTTPException(status_code=401, detail="Token validation failed")
