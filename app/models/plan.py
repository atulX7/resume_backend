from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from app.database.connection import Base


class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    duration_days = Column(Integer, nullable=False)
    is_premium = Column(Boolean, default=False)
    price = Column(Numeric(10, 2), default=0.00)
    feature_limits = Column(JSONB, default={})


class UserPlanUsage(Base):
    __tablename__ = "user_plan_usage"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False)
    expiry_date = Column(DateTime(timezone=True), nullable=True)
    usage_counts = Column(MutableDict.as_mutable(JSONB), default={})

    user = relationship("User", back_populates="user_plan")
    plan = relationship("Plan")
