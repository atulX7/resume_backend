from sqlalchemy.orm import Session
from app.models.plan import Plan, UserPlanUsage
from sqlalchemy.exc import NoResultFound
from datetime import datetime, timedelta, timezone

from app.utils.constants import FREE_PLAN_CODE


def get_all_plans(db: Session):
    return db.query(Plan).all()


def get_user_plan(db: Session, user_id: int) -> UserPlanUsage:
    return (
        db.query(UserPlanUsage)
        .filter(UserPlanUsage.user_id == user_id)
        .join(UserPlanUsage.plan)
        .first()
    )


def increment_feature_usage(db: Session, user_id: int, feature_key: str) -> bool:
    user_plan = get_user_plan(db, user_id)
    if not user_plan:
        return False

    usage = user_plan.usage_counts or {}
    usage_count = usage.get(feature_key, 0)

    limit = user_plan.plan.feature_limits.get(feature_key, 0)
    if not user_plan.plan.is_premium and usage_count >= limit:
        return False

    # Allow and increment
    usage[feature_key] = usage_count + 1
    user_plan.usage_counts = usage
    db.commit()
    db.refresh(user_plan)
    return True


def reset_usage_if_expired(db: Session, user_id: int):
    user_plan = get_user_plan(db, user_id)
    if not user_plan:
        return
    if user_plan.expiry_date and user_plan.expiry_date < datetime.now(timezone.utc):
        db.delete(user_plan)
        db.commit()


def set_user_plan(db: Session, user_id: int, plan_code: str):
    plan = db.query(Plan).filter_by(code=plan_code).first()
    if not plan:
        raise NoResultFound("Plan code not found")

    expiry = None
    if plan.duration_days > 0:
        expiry = datetime.now(timezone.utc) + timedelta(days=plan.duration_days)

    user_plan = db.query(UserPlanUsage).filter_by(user_id=user_id).first()
    if user_plan:
        user_plan.plan = plan
        user_plan.expiry_date = expiry
        user_plan.usage_counts = {}
    else:
        user_plan = UserPlanUsage(
            user_id=user_id,
            plan_id=plan.id,
            expiry_date=expiry,
            usage_counts={}
        )
        db.add(user_plan)

    db.commit()
    db.refresh(user_plan)  # ensures relationships are populated
    return user_plan


def get_plan_by_code(db: Session, plan_code: str):
    plan = db.query(Plan).filter_by(code=plan_code).first()
    if not plan:
        raise ValueError("Plan not found")
    return plan


def set_free_plan(db: Session, user_id: int):
    free_plan = get_plan_by_code(db, FREE_PLAN_CODE)
    if not free_plan:
        raise ValueError("Free plan not found")

    user_plan = UserPlanUsage(
        user_id=user_id,
        plan_id=free_plan.id,
        usage_counts={},  # initialize with zero usage
    )
    db.add(user_plan)
    db.commit()
