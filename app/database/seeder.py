from sqlalchemy.orm import Session
from app.models.auth import Role

def seed_roles(db: Session):
    """Seeds default roles if they do not exist."""
    existing_roles = db.query(Role).all()
    role_names = {role.name for role in existing_roles}

    default_roles = ["USER", "ADMIN"]

    for role_name in default_roles:
        if role_name not in role_names:
            db.add(Role(name=role_name))

    db.commit()
