import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session
from app.models.auth import User, Role
import uuid

logger = logging.getLogger("app")


def get_user_by_email(db: Session, email: str, update_last_login: bool = False):
    """Fetch a user by email"""
    """Fetch a user by email, optionally updating last_login_at"""
    logger.info(
        f"[GET_USER_BY_EMAIL] Fetching user for email: {email} | update_last_login={update_last_login}"
    )
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            logger.info(f"[GET_USER_BY_EMAIL] User found: {user.id}")
            if update_last_login:
                logger.info(
                    f"[GET_USER_BY_EMAIL] Updating last_login_at for user: {user.id}"
                )
                user.last_login_at = datetime.now(timezone.utc)
                db.commit()
        else:
            logger.warning(f"[GET_USER_BY_EMAIL] No user found for email: {email}")
        return user
    except Exception as e:
        logger.error(
            f"[GET_USER_BY_EMAIL] Error fetching user by email: {email} | {str(e)}"
        )
        return None


def get_role_by_name(db: Session, role_name: str):
    """Fetch a role by name"""
    logger.info(f"[GET_ROLE] Fetching role: {role_name}")
    try:
        role = db.query(Role).filter(Role.name == role_name).first()
        if role:
            logger.info(f"[GET_ROLE] Role found: {role.id}")
        else:
            logger.warning(f"[GET_ROLE] Role '{role_name}' not found")
        return role
    except Exception as e:
        logger.error(f"[GET_ROLE] Error fetching role '{role_name}': {str(e)}")
        return None


def get_user_by_id(db: Session, id: str):
    """Fetch a user by id"""
    logger.info(f"[GET_USER_BY_ID] Fetching user by ID: {id}")
    try:
        user = db.query(User).filter(User.id == id).first()
        if user:
            logger.info(f"[GET_USER_BY_ID] User found: {user.id}")
        else:
            logger.warning(f"[GET_USER_BY_ID] No user found for ID: {id}")
        return user
    except Exception as e:
        logger.error(f"[GET_USER_BY_ID] Error fetching user by ID {id}: {str(e)}")
        return None


def create_user(db: Session, name: str, email: str, image: str = None):
    """Create a new user"""
    logger.info(f"[CREATE_USER] Creating user with email: {email}")
    try:
        user_role = get_role_by_name(db, "USER")
        if not user_role:
            logger.error("[CREATE_USER] Default role 'USER' not found")
            raise ValueError("Default role 'USER' not found")

        user = User(
            id=str(uuid.uuid4()),
            name=name,
            email=email,
            image=image,
            role_id=user_role.id,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"[CREATE_USER] New user created with ID: {user.id}")
        return user
    except Exception as e:
        logger.error(
            f"[CREATE_USER] Failed to create user for email: {email} | {str(e)}"
        )
        raise
