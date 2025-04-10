import requests
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.database.auth import get_user_by_email, create_user
from app.database.plan import set_free_plan
from app.utils.constants import GOOGLE_USER_INFO_URL


def sync_user_service(db: Session, access_token: str):
    """Fetches user from Google and syncs with PostgreSQL."""

    # ✅ Fetch user info from Google API
    user_info = fetch_google_user(access_token)

    # ✅ Sync user in DB
    user = get_user_by_email(db, user_info["email"], update_last_login=True)
    if not user:
        user = create_user(
            db, user_info["name"], user_info["email"], user_info.get("picture")
        )
        set_free_plan(db, user.id)

    return {
        "user_id": user.id,
        "plan_code": user.user_plan.plan.code,
        "is_premium": user.has_premium_access(),
    }


def fetch_google_user(access_token: str):
    """Fetch user details from Google using access token."""
    response = requests.get(GOOGLE_USER_INFO_URL, params={"access_token": access_token})

    if response.status_code != 200:
        raise HTTPException(status_code=403, detail="Invalid Google access token")

    return response.json()
