import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.table import TableStatus


class TableBase(BaseModel):
    table_number: str = Field(min_length=1, max_length=40)
    floor: str = Field(default="Main", min_length=1, max_length=80)
    capacity: int = Field(ge=1, le=50)
    status: TableStatus = TableStatus.AVAILABLE


class TableCreate(TableBase):
    pass


class TableUpdate(BaseModel):
    table_number: str | None = Field(default=None, min_length=1, max_length=40)
    floor: str | None = Field(default=None, min_length=1, max_length=80)
    capacity: int | None = Field(default=None, ge=1, le=50)
    status: TableStatus | None = None


class TableResponse(TableBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FloorResponse(BaseModel):
    floor: str
    table_count: int
    available_count: int
    occupied_count: int
    reserved_count: int
    inactive_count: int

