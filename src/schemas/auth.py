from pydantic import BaseModel, EmailStr, Field


class RecuperarRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    password: str = Field(min_length=6)