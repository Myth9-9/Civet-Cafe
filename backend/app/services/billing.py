import uuid
from datetime import UTC, datetime
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.orm import Session

from app.models.billing import Bill, BillStatus, Payment, PaymentStatus
from app.models.order import Order, OrderStatus
from app.repositories.billing import BillRepository, PaymentRepository
from app.schemas.billing import (
    BillGenerateRequest,
    PaymentCreateRequest,
    ReceiptLineResponse,
    ReceiptResponse,
)


class BillingValidationError(ValueError):
    pass


class BillNotFoundError(ValueError):
    pass


class BillingService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._bills = BillRepository(db)
        self._payments = PaymentRepository(db)

    def list(self, *, limit: int, offset: int) -> list[Bill]:
        return list(self._bills.list(limit=limit, offset=offset))

    def get(self, bill_id: uuid.UUID) -> Bill:
        return self._require_bill(bill_id)

    def generate(self, *, payload: BillGenerateRequest, issued_by_user_id: uuid.UUID) -> Bill:
        order = self._db.get(Order, payload.order_id)
        if order is None:
            raise BillingValidationError("Order not found")
        if order.status != OrderStatus.SERVED:
            raise BillingValidationError("Only served orders can be billed")
        existing = self._bills.get_by_order_id(order.id)
        if existing is not None:
            return existing

        rounded_total = self._round_invoice_total(order.total_amount)
        bill = self._bills.add(
            Bill(
                bill_number=self._next_bill_number(),
                order_id=order.id,
                issued_by_user_id=issued_by_user_id,
                status=BillStatus.ISSUED,
                gstin=payload.gstin,
                customer_name=payload.customer_name,
                customer_phone=payload.customer_phone,
                subtotal_amount=order.subtotal_amount,
                tax_amount=order.tax_amount,
                discount_amount=order.discount_amount,
                total_amount=order.total_amount,
                rounded_total_amount=rounded_total,
            )
        )
        order.status = OrderStatus.BILLED
        self._db.commit()
        self._db.refresh(bill)
        return self._require_bill(bill.id)

    def add_payment(self, *, bill_id: uuid.UUID, payload: PaymentCreateRequest) -> Bill:
        bill = self._require_bill(bill_id)
        if bill.status == BillStatus.VOID:
            raise BillingValidationError("Cannot pay a void bill")
        if self._paid_amount(bill) + payload.amount > bill.rounded_total_amount:
            raise BillingValidationError("Payment exceeds bill total")
        self._payments.add(
            Payment(
                bill_id=bill.id,
                method=payload.method,
                status=PaymentStatus.COMPLETED,
                amount=payload.amount,
                reference_number=payload.reference_number,
            )
        )
        self._db.flush()
        self._db.refresh(bill)
        if self._paid_amount(bill) >= bill.rounded_total_amount:
            bill.status = BillStatus.PAID
        self._db.commit()
        return self._require_bill(bill.id)

    def receipt(self, bill_id: uuid.UUID) -> ReceiptResponse:
        bill = self._require_bill(bill_id)
        order = self._db.get(Order, bill.order_id)
        if order is None:
            raise BillingValidationError("Bill order is missing")
        paid_amount = self._paid_amount(bill)
        return ReceiptResponse(
            bill=bill,
            order_number=order.order_number,
            table_id=order.table_id,
            lines=[
                ReceiptLineResponse(
                    name=item.item_name_snapshot,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    tax_rate=item.tax_rate,
                    line_subtotal=item.line_subtotal,
                    line_tax=item.line_tax,
                    line_total=item.line_total,
                )
                for item in order.items
            ],
            paid_amount=paid_amount,
            balance_due=self._money(bill.rounded_total_amount - paid_amount),
        )

    def void(self, *, bill_id: uuid.UUID, reason: str) -> Bill:
        bill = self._require_bill(bill_id)
        if bill.status == BillStatus.PAID:
            raise BillingValidationError("Paid bills cannot be voided")
        bill.status = BillStatus.VOID
        bill.voided_at = datetime.now(UTC)
        bill.void_reason = reason
        self._db.commit()
        return self._require_bill(bill.id)

    def _require_bill(self, bill_id: uuid.UUID) -> Bill:
        bill = self._bills.get(bill_id)
        if bill is None:
            raise BillNotFoundError("Bill not found")
        return bill

    def _paid_amount(self, bill: Bill) -> Decimal:
        return self._money(
            sum(
                (
                    payment.amount
                    for payment in bill.payments
                    if payment.status == PaymentStatus.COMPLETED
                ),
                Decimal("0.00"),
            )
        )

    def _next_bill_number(self) -> str:
        prefix = datetime.now(UTC).strftime("BILL-%Y%m%d-")
        for sequence in range(1, 10000):
            candidate = f"{prefix}{sequence:04d}"
            if self._bills.get_by_number(candidate) is None:
                return candidate
        raise BillingValidationError("Bill sequence exhausted for today")

    def _round_invoice_total(self, amount: Decimal) -> Decimal:
        return amount.quantize(Decimal("1"), rounding=ROUND_HALF_UP)

    def _money(self, value: Decimal) -> Decimal:
        return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

