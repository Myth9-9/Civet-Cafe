from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.table import CafeTable, TableStatus
from app.repositories.tables import TableRepository
from app.schemas.tables import FloorResponse, TableCreate, TableUpdate


class TableValidationError(ValueError):
    pass


class TableNotFoundError(ValueError):
    pass


class TableService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._tables = TableRepository(db)

    def list(
        self,
        *,
        floor: str | None,
        include_inactive: bool,
        limit: int,
        offset: int,
    ) -> list[CafeTable]:
        return list(
            self._tables.list(
                floor=self._normalize_optional(floor),
                include_inactive=include_inactive,
                limit=limit,
                offset=offset,
            )
        )

    def floors(self) -> list[FloorResponse]:
        return [
            FloorResponse(
                floor=row[0],
                table_count=row[1],
                available_count=row[2],
                occupied_count=row[3],
                reserved_count=row[4],
                inactive_count=row[5],
            )
            for row in self._tables.floor_summaries()
        ]

    def create(self, payload: TableCreate) -> CafeTable:
        floor = self._normalize_required(payload.floor)
        table_number = self._normalize_required(payload.table_number)
        self._ensure_unique(floor=floor, table_number=table_number)
        table = self._tables.add(
            CafeTable(
                floor=floor,
                table_number=table_number,
                capacity=payload.capacity,
                status=payload.status,
            )
        )
        self._db.commit()
        self._db.refresh(table)
        return table

    def update(self, table_id: uuid.UUID, payload: TableUpdate) -> CafeTable:
        table = self._require_table(table_id)
        update_data = payload.model_dump(exclude_unset=True)
        next_floor = self._normalize_required(update_data.get("floor", table.floor))
        next_number = self._normalize_required(update_data.get("table_number", table.table_number))
        existing = self._tables.get_by_floor_and_number(next_floor, next_number)
        if existing and existing.id != table_id:
            raise TableValidationError("Table number already exists on this floor")
        if "floor" in update_data:
            table.floor = next_floor
        if "table_number" in update_data:
            table.table_number = next_number
        if "capacity" in update_data:
            table.capacity = update_data["capacity"]
        if "status" in update_data:
            table.status = update_data["status"]
        self._db.commit()
        self._db.refresh(table)
        return table

    def delete(self, table_id: uuid.UUID) -> None:
        table = self._require_table(table_id)
        if table.status == TableStatus.OCCUPIED:
            raise TableValidationError("Occupied tables cannot be deleted")
        table.deleted_at = datetime.now(UTC)
        table.status = TableStatus.INACTIVE
        self._db.commit()

    def _require_table(self, table_id: uuid.UUID) -> CafeTable:
        table = self._tables.get_active(table_id)
        if table is None:
            raise TableNotFoundError("Table not found")
        return table

    def _ensure_unique(self, *, floor: str, table_number: str) -> None:
        if self._tables.get_by_floor_and_number(floor, table_number):
            raise TableValidationError("Table number already exists on this floor")

    def _normalize_required(self, value: object) -> str:
        normalized = str(value).strip()
        if not normalized:
            raise TableValidationError("Floor and table number are required")
        return normalized

    def _normalize_optional(self, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None

