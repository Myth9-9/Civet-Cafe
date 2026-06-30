import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.billing import Bill, Payment


class BillRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list(self, *, limit: int, offset: int) -> Sequence[Bill]:
        statement = (
            select(Bill)
            .options(selectinload(Bill.payments))
            .order_by(Bill.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return self._db.execute(statement).scalars().all()

    def get(self, bill_id: uuid.UUID) -> Bill | None:
        statement = select(Bill).options(selectinload(Bill.payments)).where(Bill.id == bill_id)
        return self._db.execute(statement).scalar_one_or_none()

    def get_by_order_id(self, order_id: uuid.UUID) -> Bill | None:
        statement = select(Bill).options(selectinload(Bill.payments)).where(Bill.order_id == order_id)
        return self._db.execute(statement).scalar_one_or_none()

    def get_by_number(self, bill_number: str) -> Bill | None:
        statement = select(Bill).where(Bill.bill_number == bill_number)
        return self._db.execute(statement).scalar_one_or_none()

    def add(self, bill: Bill) -> Bill:
        self._db.add(bill)
        self._db.flush()
        return bill


class PaymentRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def add(self, payment: Payment) -> Payment:
        self._db.add(payment)
        self._db.flush()
        return payment

