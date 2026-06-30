import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SettingUpsert(BaseModel):
    key: str = Field(min_length=2, max_length=120, pattern=r"^[a-z0-9_.-]+$")
    value: dict[str, Any]
    is_public: bool = False


class SettingUpdate(BaseModel):
    value: dict[str, Any] | None = None
    is_public: bool | None = None


class SettingResponse(BaseModel):
    id: uuid.UUID
    key: str
    value: dict[str, Any]
    is_public: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

