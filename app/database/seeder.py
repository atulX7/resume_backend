import logging

from sqlalchemy.orm import Session
from app.models.auth import Role
from app.models.plan import Plan

logger = logging.getLogger("app")

default_plans = [
    {
        "code": "free",
        "name": "Free Plan",
        "duration_days": 10,
        "is_premium": False,
        "price": 0.0,
        "feature_limits": {
            "resume_eval": 5,
            "resume_tailor": 5,
            "mock_interview": 5
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
    logger.info("[DB_INIT] 🌱 Starting plan seeding...")
    try:
        for plan_data in default_plans:
            plan = db.query(Plan).filter_by(code=plan_data["code"]).first()
            if plan:
                logger.info(f"[DB_INIT] 🔄 Updating existing plan: {plan.code}")
                for key, value in plan_data.items():
                    setattr(plan, key, value)
            else:
                logger.info(f"[DB_INIT] 🆕 Adding new plan: {plan_data['code']}")
                db.add(Plan(**plan_data))

        db.commit()
        logger.info("[DB_INIT] ✅ Plans seeding completed successfully.")
    except Exception as e:
        logger.error(f"[DB_INIT] ❌ Error seeding plans: {str(e)}", exc_info=True)
        db.rollback()


def seed_roles(db: Session):
    """Seeds default roles if they do not exist."""
    logger.info("[DB_INIT] 🌱 Starting role seeding...")
    try:
        existing_roles = db.query(Role).all()
        role_names = {role.name for role in existing_roles}
        default_roles = ["USER", "ADMIN"]

        for role_name in default_roles:
            if role_name not in role_names:
                logger.info(f"[DB_INIT] 🆕 Adding new role: {role_name}")
                db.add(Role(name=role_name))
            else:
                logger.info(f"[DB_INIT] ✅ Role already exists: {role_name}")

        db.commit()
        logger.info("[DB_INIT] ✅ Roles seeding completed successfully.")
    except Exception as e:
        logger.error(f"[DB_INIT] ❌ Error seeding roles: {str(e)}", exc_info=True)
        db.rollback()


def initialize_db(db: Session):
    logger.info("[DB_INIT] 🔧 Initializing DB with roles and plans...")
    try:
        seed_roles(db)
        seed_plans(db)
        logger.info("[DB_INIT] 🎉 DB initialization completed.")
    except Exception as e:
        logger.error(f"[DB_INIT] ❌ DB initialization failed: {str(e)}", exc_info=True)
