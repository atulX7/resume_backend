import logging

import requests
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.database.auth import get_user_by_email, create_user
from app.database.plan import set_free_plan
from app.utils.constants import GOOGLE_USER_INFO_URL

logger = logging.getLogger("app")


def sync_user_service(db: Session, access_token: str):
    """Fetches user from Google and syncs with PostgreSQL."""
    logger.info("[AUTH] Starting user sync from Google.")

    try:
        # ✅ Step 1: Get user info from Google
        user_info = fetch_google_user(access_token)
        email = user_info.get("email")

        if not email:
            logger.error("[AUTH] Email missing in Google response.")
            raise HTTPException(
                status_code=400, detail="Email not found in Google user info"
            )

        logger.info(f"[AUTH] Fetched Google user profile for email: {email}")

        # ✅ Step 2: Sync user in DB
        user = get_user_by_email(db, email, update_last_login=True)
        if user:
            logger.info(f"[AUTH] Existing user found: {user.id}. Last login updated.")
        else:
            logger.info(f"[AUTH] No user found. Creating new user for email: {email}")
            user = create_user(db, user_info["name"], email, user_info.get("picture"))
            logger.info(f"[AUTH] New user created: {user.id}. Assigning free plan.")
            set_free_plan(db, user.id)
            logger.info(f"[AUTH] Free plan assigned to user: {user.id}")

        return {
            "user_id": user.id,
            "plan_code": user.user_plan.plan.code,
            "is_premium": user.has_premium_access(),
        }

    except HTTPException as e:
        logger.error(f"[AUTH] HTTP error while syncing user: {e.detail}")
        raise
    except Exception as e:
        logger.exception(f"[AUTH] Unexpected error during user sync: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


def fetch_google_user(access_token: str):
    """Fetch user details from Google using access token."""
    logger.info("[AUTH] Validating Google access token.")

    try:
        response = requests.get(
            GOOGLE_USER_INFO_URL, params={"access_token": access_token}
        )

        if response.status_code != 200:
            logger.warning(f"[AUTH] Invalid access token. Response: {response.text}")
            raise HTTPException(status_code=403, detail="Invalid Google access token")

        logger.info("[AUTH] Google access token validated successfully.")
        return response.json()

    except requests.RequestException as e:
        logger.exception("[AUTH] Error while contacting Google OAuth endpoint.")
        raise HTTPException(status_code=502, detail="Failed to contact Google OAuth")
