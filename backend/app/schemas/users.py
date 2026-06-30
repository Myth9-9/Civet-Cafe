import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RoleResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    is_system: bool

    model_config = ConfigDict(from_attributes=True)


class PermissionResponse(BaseModel):
    id: uuid.UUID
    code: str
    module: str
    action: str
    description: str | None

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=160)
    role_id: uuid.UUID
    supabase_user_id: uuid.UUID | None = None
    phone: str | None = Field(default=None, max_length=32)
    employee_code: str | None = Field(default=None, max_length=40)
    is_active: bool = True


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=160)
    role_id: uuid.UUID | None = None
    supabase_user_id: uuid.UUID | None = None
    phone: str | None = Field(default=None, max_length=32)
    employee_code: str | None = Field(default=None, max_length=40)
    is_active: bool | None = None


class UserResponse(BaseModel):
    id: uuid.UUID
    supabase_user_id: uuid.UUID | None
    role_id: uuid.UUID
    email: EmailStr
    full_name: str
    phone: str | None
    employee_code: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

