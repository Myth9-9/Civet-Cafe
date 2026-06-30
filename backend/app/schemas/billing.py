import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.billing import BillStatus, PaymentMethod, PaymentStatus


class BillGenerateRequest(BaseModel):
    order_id: uuid.UUID
    customer_name: str | None = Field(default=None, max_length=160)
    customer_phone: str | None = Field(default=None, max_length=32)
    gstin: str | None = Field(default=None, max_length=32)


class PaymentCreateRequest(BaseModel):
    method: PaymentMethod
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    reference_number: str | None = Field(default=None, max_length=120)


class PaymentResponse(BaseModel):
    id: uuid.UUID
    bill_id: uuid.UUID
    method: PaymentMethod
    status: PaymentStatus
    amount: Decimal
    reference_number: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BillResponse(BaseModel):
    id: uuid.UUID
    bill_number: str
    order_id: uuid.UUID
    issued_by_user_id: uuid.UUID
    status: BillStatus
    gstin: str | None
    customer_name: str | None
    customer_phone: str | None
    subtotal_amount: Decimal
    tax_amount: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    rounded_total_amount: Decimal
    voided_at: datetime | None
    void_reason: str | None
    created_at: datetime
    updated_at: datetime
    payments: list[PaymentResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ReceiptLineResponse(BaseModel):
    name: str
    quantity: int
    unit_price: Decimal
    tax_rate: Decimal
    line_subtotal: Decimal
    line_tax: Decimal
    line_total: Decimal


class ReceiptResponse(BaseModel):
    bill: BillResponse
    order_number: str
    table_id: uuid.UUID | None
    lines: list[ReceiptLineResponse]
    paid_amount: Decimal
    balance_due: Decimal

