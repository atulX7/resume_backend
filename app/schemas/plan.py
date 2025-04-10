from pydantic import BaseModel, validator
from typing import Optional, Dict
from datetime import datetime


class PlanSchema(BaseModel):
    code: str
    name: str
    duration_days: int
    is_premium: bool
    price: float
    feature_limits: Dict[str, int]

    class Config:
        orm_mode = True


class UserPlanUsageSchema(BaseModel):
    user_id: str
    plan: PlanSchema
    usage_counts: Dict[str, int]
    expiry_date: Optional[str]

    class Config:
        orm_mode = True

    @validator("expiry_date", pre=True, always=True)
    def format_expiry_date(cls, value):
        if isinstance(value, datetime):
            return value.strftime("%Y/%m/%d")
        return value
