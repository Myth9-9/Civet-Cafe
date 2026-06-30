import enum
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, enum_values
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class BillStatus(str, enum.Enum):
    ISSUED = "issued"
    PAID = "paid"
    VOID = "void"


class PaymentMethod(str, enum.Enum):
    CASH = "cash"
    CARD = "card"
    UPI = "upi"
    WALLET = "wallet"
    MIXED = "mixed"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class Bill(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "bills"

    bill_number: Mapped[str] = mapped_column(String(40), nullable=False, unique=True)
    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="RESTRICT"),
        nullable=False,
        unique=True,
    )
    issued_by_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    status: Mapped[BillStatus] = mapped_column(
        Enum(BillStatus, name="bill_status", values_callable=enum_values),
        nullable=False,
        server_default=BillStatus.ISSUED.value,
    )
    gstin: Mapped[str | None] = mapped_column(String(32), nullable=True)
    customer_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    customer_phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    subtotal_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    discount_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        server_default="0",
    )
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    rounded_total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    voided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    void_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    payments: Mapped[list["Payment"]] = relationship(
        back_populates="bill",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_bills_order_id", "order_id"),
        Index("ix_bills_issued_by_user_id", "issued_by_user_id"),
        Index("ix_bills_status_created_at", "status", "created_at"),
        Index("ix_bills_created_at", "created_at"),
    )


class Payment(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "payments"

    bill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("bills.id", ondelete="CASCADE"),
        nullable=False,
    )
    method: Mapped[PaymentMethod] = mapped_column(
        Enum(PaymentMethod, name="payment_method", values_callable=enum_values),
        nullable=False,
    )
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus, name="payment_status", values_callable=enum_values),
        nullable=False,
        server_default=PaymentStatus.PENDING.value,
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    reference_number: Mapped[str | None] = mapped_column(String(120), nullable=True)
    provider_response: Mapped[str | None] = mapped_column(Text, nullable=True)

    bill: Mapped[Bill] = relationship(back_populates="payments")

    __table_args__ = (
        Index("ix_payments_bill_id", "bill_id"),
        Index("ix_payments_method_status", "method", "status"),
        Index("ix_payments_created_at", "created_at"),
    )

