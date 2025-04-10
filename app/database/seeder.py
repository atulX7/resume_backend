from sqlalchemy.orm import Session
from app.models.auth import Role
from app.models.plan import Plan

default_plans = [
    {
        "code": "free",
        "name": "Free Plan",
        "duration_days": 10,
        "is_premium": False,
        "price": 0.0,
        "feature_limits": {
            "resume_eval": 2,
            "resume_tailor": 2,
            "mock_interview": 1
        },
    },
    {
        "code": "prem_mon",
        "name": "Premium Monthly",
        "duration_days": 30,
        "is_premium": True,
        "price": 49,
        "feature_limits": {
            "resume_eval": -1,
            "resume_tailor": -1,
            "mock_interview": -1,
        },
    },
    {
        "code": "prem_year",
        "name": "Premium Yearly",
        "duration_days": 365,
        "is_premium": True,
        "price": 99,
        "feature_limits": {
            "resume_eval": -1,
            "resume_tailor": -1,
            "mock_interview": -1,
        },
    },
]


def seed_plans(db: Session):
    for plan_data in default_plans:
        plan = db.query(Plan).filter_by(code=plan_data["code"]).first()
        if plan:
            for key, value in plan_data.items():
                setattr(plan, key, value)
        else:
            db.add(Plan(**plan_data))
    db.commit()


def seed_roles(db: Session):
    """Seeds default roles if they do not exist."""
    existing_roles = db.query(Role).all()
    role_names = {role.name for role in existing_roles}

    default_roles = ["USER", "ADMIN"]

    for role_name in default_roles:
        if role_name not in role_names:
            db.add(Role(name=role_name))

    db.commit()


def initialize_db(db: Session):
    seed_roles(db)
    seed_plans(db)
