from datetime import date
from decimal import Decimal

from pydantic import BaseModel

from app.models.billing import PaymentMethod


class PaymentMethodTotal(BaseModel):
    method: PaymentMethod
    amount: Decimal


class SalesReportResponse(BaseModel):
    period_start: date
    period_end: date
    bill_count: int
    paid_bill_count: int
    gross_sales: Decimal
    net_sales: Decimal
    tax_collected: Decimal
    discounts: Decimal
    payments_collected: Decimal
    average_bill_value: Decimal
    payment_methods: list[PaymentMethodTotal]

