from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.billing import Bill, BillStatus, Payment, PaymentStatus


class ReportsRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def bill_totals(self, *, start_at: datetime, end_at: datetime) -> tuple[int, int, Decimal, Decimal, Decimal]:
        statement = select(
            func.count(Bill.id),
            func.count(Bill.id).filter(Bill.status == BillStatus.PAID),
            func.coalesce(func.sum(Bill.rounded_total_amount).filter(Bill.status == BillStatus.PAID), 0),
            func.coalesce(func.sum(Bill.tax_amount).filter(Bill.status == BillStatus.PAID), 0),
            func.coalesce(func.sum(Bill.discount_amount).filter(Bill.status == BillStatus.PAID), 0),
        ).where(Bill.created_at >= start_at, Bill.created_at < end_at)
        row = self._db.execute(statement).one()
        return (
            int(row[0] or 0),
            int(row[1] or 0),
            Decimal(row[2] or 0),
            Decimal(row[3] or 0),
            Decimal(row[4] or 0),
        )

    def payment_total(self, *, start_at: datetime, end_at: datetime) -> Decimal:
        statement = (
            select(func.coalesce(func.sum(Payment.amount), 0))
            .join(Bill, Bill.id == Payment.bill_id)
            .where(Payment.status == PaymentStatus.COMPLETED)
            .where(Payment.created_at >= start_at, Payment.created_at < end_at)
        )
        return Decimal(self._db.execute(statement).scalar_one() or 0)

    def payment_method_totals(self, *, start_at: datetime, end_at: datetime) -> list[tuple[str, Decimal]]:
        statement = (
            select(Payment.method, func.coalesce(func.sum(Payment.amount), 0))
            .join(Bill, Bill.id == Payment.bill_id)
            .where(Payment.status == PaymentStatus.COMPLETED)
            .where(Payment.created_at >= start_at, Payment.created_at < end_at)
            .group_by(Payment.method)
            .order_by(Payment.method)
        )
        return [(row[0].value if hasattr(row[0], "value") else str(row[0]), Decimal(row[1] or 0)) for row in self._db.execute(statement).all()]

