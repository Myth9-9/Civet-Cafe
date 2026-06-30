import uuid
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.table import CafeTable, TableStatus


class TableRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list(
        self,
        *,
        floor: str | None,
        include_inactive: bool,
        limit: int,
        offset: int,
    ) -> Sequence[CafeTable]:
        statement = (
            select(CafeTable)
            .where(CafeTable.deleted_at.is_(None))
            .order_by(CafeTable.floor, CafeTable.table_number)
            .limit(limit)
            .offset(offset)
        )
        if floor:
            statement = statement.where(CafeTable.floor == floor)
        if not include_inactive:
            statement = statement.where(CafeTable.status != TableStatus.INACTIVE)
        return self._db.execute(statement).scalars().all()

    def get_active(self, table_id: uuid.UUID) -> CafeTable | None:
        statement = select(CafeTable).where(CafeTable.id == table_id).where(CafeTable.deleted_at.is_(None))
        return self._db.execute(statement).scalar_one_or_none()

    def get_by_floor_and_number(self, floor: str, table_number: str) -> CafeTable | None:
        statement = (
            select(CafeTable)
            .where(CafeTable.floor == floor)
            .where(CafeTable.table_number == table_number)
            .where(CafeTable.deleted_at.is_(None))
        )
        return self._db.execute(statement).scalar_one_or_none()

    def floor_summaries(self) -> Sequence[tuple[str, int, int, int, int, int]]:
        available = func.count().filter(CafeTable.status == TableStatus.AVAILABLE)
        occupied = func.count().filter(CafeTable.status == TableStatus.OCCUPIED)
        reserved = func.count().filter(CafeTable.status == TableStatus.RESERVED)
        inactive = func.count().filter(CafeTable.status == TableStatus.INACTIVE)
        statement = (
            select(CafeTable.floor, func.count(), available, occupied, reserved, inactive)
            .where(CafeTable.deleted_at.is_(None))
            .group_by(CafeTable.floor)
            .order_by(CafeTable.floor)
        )
        return self._db.execute(statement).all()

    def add(self, table: CafeTable) -> CafeTable:
        self._db.add(table)
        self._db.flush()
        return table

