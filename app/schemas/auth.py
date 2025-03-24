from pydantic import BaseModel

class SyncUserRequest(BaseModel):
    access_token: str

class SyncUserResponse(BaseModel):
    user_id: str
    plan_code: str
    is_premium: bool

