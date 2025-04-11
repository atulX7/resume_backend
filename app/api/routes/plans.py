import logging

from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from app.schemas.plan import PlanSchema, UserPlanUsageSchema
from app.database.connection import get_db
from app.database.plan import get_all_plans, get_user_plan, set_user_plan
from app.middleware.auth_dependency import get_current_user

router = APIRouter()

logger = logging.getLogger("app")


@router.get("/", response_model=list[PlanSchema])
def list_all_plans(db: Session = Depends(get_db)):
    try:
        logger.info("[PLAN] Fetching all available plans")
        plans = get_all_plans(db)
        logger.info(f"[PLAN] Retrieved {len(plans)} plans")
        return plans
    except Exception as e:
        logger.error(f"[PLAN] Failed to fetch plans: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve plans")


@router.get("/my-plan", response_model=UserPlanUsageSchema)
def get_my_plan(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        logger.info(f"[MY_PLAN] Fetching plan for user: {current_user.id}")
        plan = get_user_plan(db, current_user.id)
        if not plan:
            logger.warning(
                f"[MY_PLAN] No active plan found for user: {current_user.id}"
            )
            raise HTTPException(status_code=404, detail="User has no active plan")
        logger.info(
            f"[MY_PLAN] Found plan '{plan.plan.code}' for user: {current_user.id}"
        )
        return plan
    except Exception as e:
        logger.error(
            f"[MY_PLAN] Failed to fetch plan for user {current_user.id}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Failed to retrieve user plan")


@router.post("/subscribe", response_model=UserPlanUsageSchema)
def subscribe_to_plan(
    plan_code: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        logger.info(
            f"[SUBSCRIBE] User {current_user.id} subscribing to plan: {plan_code}"
        )
        user_plan = set_user_plan(db, current_user.id, plan_code)
        logger.info(
            f"[SUBSCRIBE] User {current_user.id} successfully subscribed to: {plan_code}"
        )
        return user_plan
    except Exception as e:
        logger.error(
            f"[SUBSCRIBE] Failed to subscribe user {current_user.id} to plan {plan_code}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Failed to subscribe to plan")
