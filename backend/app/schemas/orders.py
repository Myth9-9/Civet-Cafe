import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.order import OrderStatus


class OrderItemCreate(BaseModel):
    menu_item_id: uuid.UUID
    quantity: int = Field(ge=1, le=100)
    notes: str | None = Field(default=None, max_length=1000)


class OrderItemResponse(BaseModel):
    id: uuid.UUID
    order_id: uuid.UUID
    menu_item_id: uuid.UUID | None
    item_name_snapshot: str
    unit_price: Decimal
    tax_rate: Decimal
    quantity: int
    line_subtotal: Decimal
    line_tax: Decimal
    line_total: Decimal
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrderCreate(BaseModel):
    table_id: uuid.UUID | None = None
    items: list[OrderItemCreate] = Field(default_factory=list)
    notes: str | None = Field(default=None, max_length=2000)


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class OrderResponse(BaseModel):
    id: uuid.UUID
    order_number: str
    table_id: uuid.UUID | None
    created_by_user_id: uuid.UUID
    status: OrderStatus
    subtotal_amount: Decimal
    tax_amount: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    notes: str | None
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class AddOrderItemRequest(OrderItemCreate):
    pass


class UpdateOrderItemRequest(BaseModel):
    quantity: int | None = Field(default=None, ge=1, le=100)
    notes: str | None = Field(default=None, max_length=1000)

