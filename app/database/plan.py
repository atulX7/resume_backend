import logging

from sqlalchemy.orm import Session
from app.models.plan import Plan, UserPlanUsage
from sqlalchemy.exc import NoResultFound
from datetime import datetime, timedelta, timezone

from app.utils.constants import FREE_PLAN_CODE

logger = logging.getLogger("app")


def get_all_plans(db: Session):
    logger.info("[PLAN] Fetching all plans from the database.")
    try:
        return db.query(Plan).all()
    except Exception as e:
        logger.error(f"[PLAN] Failed to fetch plans. Error: {str(e)}")
        raise


def get_user_plan(db: Session, user_id: int) -> UserPlanUsage:
    logger.info(f"[PLAN] Fetching plan for user: {user_id}")
    try:
        plan = (
            db.query(UserPlanUsage)
            .filter(UserPlanUsage.user_id == user_id)
            .join(UserPlanUsage.plan)
            .first()
        )
        if not plan:
            logger.warning(f"[PLAN] No plan found for user: {user_id}")
        return plan
    except Exception as e:
        logger.error(f"[PLAN] Failed to retrieve user plan. Error: {str(e)}")
        raise


def increment_feature_usage(db: Session, user_id: int, feature_key: str) -> bool:
    logger.info(f"[PLAN_USAGE] Checking usage for feature '{feature_key}' for user: {user_id}")
    user_plan = get_user_plan(db, user_id)
    if not user_plan:
        logger.warning(f"[PLAN_USAGE] No active plan found for user: {user_id}")
        return False

    usage = user_plan.usage_counts or {}
    usage_count = usage.get(feature_key, 0)
    logger.info(f"[PLAN_USAGE] Current count: {usage_count} | Limit: {user_plan.plan.feature_limits.get(feature_key)}")

    limit = user_plan.plan.feature_limits.get(feature_key, 0)
    is_premium_user = user_plan.plan.is_premium

    if not is_premium_user and usage_count >= limit:
        logger.warning(f"[PLAN_USAGE] Feature '{feature_key}' blocked for user: {user_id}. Limit reached.")
        return False

    usage[feature_key] = usage_count + 1
    user_plan.usage_counts = usage

    try:
        db.commit()
        db.refresh(user_plan)
        logger.info(f"[PLAN_USAGE] Usage incremented for feature '{feature_key}' for user: {user_id}")
        return True
    except Exception as e:
        logger.error(f"[PLAN_USAGE] Failed to increment usage. Error: {str(e)}")
        raise


def set_user_plan(db: Session, user_id: int, plan_code: str):
    logger.info(f"[PLAN] Setting plan '{plan_code}' for user: {user_id}")
    plan = db.query(Plan).filter_by(code=plan_code).first()
    if not plan:
        logger.warning(f"[PLAN] Plan code '{plan_code}' not found.")
        raise NoResultFound("Plan code not found")

    expiry = None
    if plan.duration_days > 0:
        expiry = datetime.now(timezone.utc) + timedelta(days=plan.duration_days)
        logger.info(f"[PLAN] Calculated expiry date: {expiry} for plan: {plan_code}")

    user_plan = db.query(UserPlanUsage).filter_by(user_id=user_id).first()
    if user_plan:
        logger.info(f"[PLAN] Updating existing plan for user: {user_id}")
        user_plan.plan = plan
        user_plan.expiry_date = expiry
        user_plan.usage_counts = {}
    else:
        logger.info(f"[PLAN] Creating new plan assignment for user: {user_id}")
        user_plan = UserPlanUsage(
            user_id=user_id,
            plan_id=plan.id,
            expiry_date=expiry,
            usage_counts={},
        )
        db.add(user_plan)

    try:
        db.commit()
        db.refresh(user_plan)
        logger.info(f"[PLAN] Plan '{plan_code}' assigned to user: {user_id}")
        return user_plan
    except Exception as e:
        logger.error(f"[PLAN] Failed to set plan '{plan_code}' for user: {user_id}. Error: {str(e)}")
        raise


def get_plan_by_code(db: Session, plan_code: str):
    logger.info(f"[PLAN] Retrieving plan by code: {plan_code}")
    plan = db.query(Plan).filter_by(code=plan_code).first()
    if not plan:
        logger.warning(f"[PLAN] Plan with code '{plan_code}' not found.")
        raise ValueError("Plan not found")
    return plan


def set_free_plan(db: Session, user_id: int):
    logger.info(f"[PLAN] Assigning free plan to user: {user_id}")
    free_plan = get_plan_by_code(db, FREE_PLAN_CODE)
    if not free_plan:
        logger.warning(f"[PLAN] Free plan '{FREE_PLAN_CODE}' not found.")
        raise ValueError("Free plan not found")

    try:
        user_plan = UserPlanUsage(
            user_id=user_id,
            plan_id=free_plan.id,
            usage_counts={},
        )
        db.add(user_plan)
        db.commit()
        logger.info(f"[PLAN] Free plan successfully assigned to user: {user_id}")
    except Exception as e:
        logger.error(f"[PLAN] Failed to assign free plan to user: {user_id}. Error: {str(e)}")
        raise
