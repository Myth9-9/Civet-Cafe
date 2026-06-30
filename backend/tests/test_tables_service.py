from __future__ import annotations

import uuid
import pytest

from app.models.table import CafeTable, TableStatus
from app.services.tables import TableService, TableValidationError, TableNotFoundError
from app.schemas.tables import TableCreate, TableUpdate


def test_create_table_succeeds(db):
    service = TableService(db)
    payload = TableCreate(
        table_number="T1",
        floor="Ground Floor",
        capacity=4,
        status=TableStatus.AVAILABLE,
    )
    table = service.create(payload)

    assert table.table_number == "T1"
    assert table.floor == "Ground Floor"
    assert table.capacity == 4
    assert table.status == TableStatus.AVAILABLE
    assert table.id is not None


def test_create_table_duplicate_number_on_same_floor_raises_error(db):
    # Seed a table
    table = CafeTable(
        id=uuid.uuid4(),
        table_number="T2",
        floor="Main Hall",
        capacity=2,
    )
    db.add(table)
    db.commit()

    service = TableService(db)
    payload = TableCreate(
        table_number="T2",
        floor="Main Hall",
        capacity=4,
    )
    with pytest.raises(TableValidationError) as exc_info:
        service.create(payload)
    assert "already exists on this floor" in str(exc_info.value)


def test_create_table_same_number_different_floors_succeeds(db):
    table = CafeTable(
        id=uuid.uuid4(),
        table_number="T2",
        floor="Main Hall",
        capacity=2,
    )
    db.add(table)
    db.commit()

    service = TableService(db)
    payload = TableCreate(
        table_number="T2",
        floor="Terrace",
        capacity=4,
    )
    created = service.create(payload)
    assert created.table_number == "T2"
    assert created.floor == "Terrace"


def test_update_table(db):
    table_id = uuid.uuid4()
    table = CafeTable(
        id=table_id,
        table_number="T3",
        floor="Main Hall",
        capacity=2,
        status=TableStatus.AVAILABLE,
    )
    db.add(table)
    db.commit()

    service = TableService(db)
    payload = TableUpdate(capacity=6, status=TableStatus.OCCUPIED)
    updated = service.update(table_id, payload)

    assert updated.capacity == 6
    assert updated.status == TableStatus.OCCUPIED


def test_delete_occupied_table_raises_error(db):
    table_id = uuid.uuid4()
    table = CafeTable(
        id=table_id,
        table_number="T4",
        floor="Main Hall",
        capacity=4,
        status=TableStatus.OCCUPIED,
    )
    db.add(table)
    db.commit()

    service = TableService(db)
    with pytest.raises(TableValidationError) as exc_info:
        service.delete(table_id)
    assert "Occupied tables cannot be deleted" in str(exc_info.value)


def test_delete_available_table_soft_deletes(db):
    table_id = uuid.uuid4()
    table = CafeTable(
        id=table_id,
        table_number="T5",
        floor="Main Hall",
        capacity=4,
        status=TableStatus.AVAILABLE,
    )
    db.add(table)
    db.commit()

    service = TableService(db)
    service.delete(table_id)

    # Verify soft deleted status
    deleted_table = db.get(CafeTable, table_id)
    assert deleted_table.deleted_at is not None
    assert deleted_table.status == TableStatus.INACTIVE


class TestTableEdgeCases:
    def test_update_table_not_found_raises_error(self, db):
        svc = TableService(db)
        with pytest.raises(TableNotFoundError):
            svc.update(uuid.uuid4(), TableUpdate(capacity=6))

    def test_delete_table_not_found_raises_error(self, db):
        svc = TableService(db)
        with pytest.raises(TableNotFoundError):
            svc.delete(uuid.uuid4())

    def test_list_tables_filters_by_floor(self, db):
        db.add(CafeTable(id=uuid.uuid4(), table_number="GF-1", floor="Ground Floor", capacity=2))
        db.add(CafeTable(id=uuid.uuid4(), table_number="GF-2", floor="Ground Floor", capacity=4))
        db.add(CafeTable(id=uuid.uuid4(), table_number="FF-1", floor="First Floor", capacity=6))
        db.commit()

        svc = TableService(db)
        ground = svc.list(floor="Ground Floor", include_inactive=False, limit=10, offset=0)
        assert len(ground) == 2
        assert all(t.floor == "Ground Floor" for t in ground)

    def test_floors(self, db):
        db.add(CafeTable(id=uuid.uuid4(), table_number="T1", floor="Main", capacity=2, status=TableStatus.AVAILABLE))
        db.add(CafeTable(id=uuid.uuid4(), table_number="T2", floor="Main", capacity=4, status=TableStatus.OCCUPIED))
        db.add(CafeTable(id=uuid.uuid4(), table_number="T3", floor="Terrace", capacity=6, status=TableStatus.INACTIVE))
        db.commit()

        svc = TableService(db)
        floors = svc.floors()
        floor_map = {f.floor: f for f in floors}

        assert "Main" in floor_map
        assert "Terrace" in floor_map
        assert floor_map["Main"].table_count == 2
        assert floor_map["Main"].available_count == 1
        assert floor_map["Main"].occupied_count == 1
