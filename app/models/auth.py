from sqlalchemy import Column, String, ForeignKey, DateTime
from datetime import datetime, timezone
import uuid
from app.database.connection import Base
from sqlalchemy.orm import relationship


class Role(Base):
    """Stores user roles like USER, ADMIN"""
    __tablename__ = "roles"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, nullable=False)


class User(Base):
    """User table"""
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=False)
    image = Column(String, nullable=True)
    role_id = Column(String, ForeignKey("roles.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    role = relationship("Role")


class Account(Base):
    """Stores linked accounts for users"""
    __tablename__ = "accounts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    provider = Column(String, nullable=False)  # "google", "linkedin"
    provider_account_id = Column(String, nullable=False)


class JWTBlacklist(Base):
    """Blacklist JWT Tokens (for logout)"""
    __tablename__ = "jwt_blacklist"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    token = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
