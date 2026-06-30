import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=256)


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(min_length=32)


class LogoutRequest(BaseModel):
    refresh_token: str = Field(min_length=32)


class AuthUserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str
    role_id: uuid.UUID
    role_name: str
    permissions: list[str]


class TokenPairResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_at: datetime
    user: AuthUserResponse


class MessageResponse(BaseModel):
    message: str


class CurrentUserPrincipal(BaseModel):
    user_id: uuid.UUID
    email: EmailStr
    role_id: uuid.UUID
    role_name: str
    permissions: frozenset[str]

