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
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_login_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    role = relationship("Role")
    user_plan = relationship("UserPlanUsage", back_populates="user", uselist=False)

    def has_premium_access(self):
        """Check if user has an active premium plan."""
        return self.user_plan and self.user_plan.plan.is_premium and (
                    self.user_plan.expiry_date is None or self.user_plan.expiry_date > datetime.now(timezone.utc))


