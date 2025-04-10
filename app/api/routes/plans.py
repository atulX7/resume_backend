from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from app.schemas.plan import PlanSchema, UserPlanUsageSchema
from app.database.connection import get_db
from app.database.plan import get_all_plans, get_user_plan, set_user_plan
from app.middleware.auth_dependency import get_current_user

router = APIRouter()


@router.get("/", response_model=list[PlanSchema])
def list_all_plans(db: Session = Depends(get_db)):
    return get_all_plans(db)


@router.get("/my-plan", response_model=UserPlanUsageSchema)
def get_my_plan(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    plan = get_user_plan(db, current_user.id)
    if not plan:
        raise HTTPException(status_code=404, detail="User has no active plan")
    return plan


@router.post("/subscribe", response_model=UserPlanUsageSchema)
def subscribe_to_plan(
    plan_code: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user_plan = set_user_plan(db, current_user.id, plan_code)
    return user_plan
