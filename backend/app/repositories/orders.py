import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.order import Order, OrderItem, OrderStatus


class OrderRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list(
        self,
        *,
        status: OrderStatus | None,
        table_id: uuid.UUID | None,
        limit: int,
        offset: int,
    ) -> Sequence[Order]:
        statement = (
            select(Order)
            .options(selectinload(Order.items))
            .order_by(Order.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        if status is not None:
            statement = statement.where(Order.status == status)
        if table_id is not None:
            statement = statement.where(Order.table_id == table_id)
        return self._db.execute(statement).scalars().all()

    def get(self, order_id: uuid.UUID) -> Order | None:
        statement = select(Order).options(selectinload(Order.items)).where(Order.id == order_id)
        return self._db.execute(statement).scalar_one_or_none()

    def get_by_number(self, order_number: str) -> Order | None:
        statement = select(Order).where(Order.order_number == order_number)
        return self._db.execute(statement).scalar_one_or_none()

    def add(self, order: Order) -> Order:
        self._db.add(order)
        self._db.flush()
        return order


class OrderItemRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get(self, item_id: uuid.UUID) -> OrderItem | None:
        return self._db.get(OrderItem, item_id)

    def add(self, item: OrderItem) -> OrderItem:
        self._db.add(item)
        self._db.flush()
        return item

    def delete(self, item: OrderItem) -> None:
        self._db.delete(item)
        self._db.flush()

