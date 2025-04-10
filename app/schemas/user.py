from pydantic import BaseModel, EmailStr


class OAuthUserSchema(BaseModel):
    email: EmailStr
    full_name: str
    provider: str  # google/linkedin
    provider_id: str


class UserRegister(BaseModel):
    email: EmailStr
    password: str
