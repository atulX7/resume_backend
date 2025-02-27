from sqlalchemy.orm import Session
from app.models.auth import User, Role
import uuid

def get_user_by_email(db: Session, email: str):
    """Fetch a user by email"""
    return db.query(User).filter(User.email == email).first()

def get_role_by_name(db: Session, role_name: str):
    """Fetch a role by name"""
    return db.query(Role).filter(Role.name == role_name).first()

def get_user_by_id(db: Session, id: str):
    """Fetch a user by id"""
    return db.query(User).filter(User.id == id).first()

def create_user(db: Session, name: str, email: str, image: str = None):
    """Create a new user"""
    user_role = get_role_by_name(db, "USER")
    if not user_role:
        raise ValueError("Default role 'USER' not found")

    user = User(
        id=str(uuid.uuid4()),
        name=name,
        email=email,
        image=image,
        role_id=user_role.id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
