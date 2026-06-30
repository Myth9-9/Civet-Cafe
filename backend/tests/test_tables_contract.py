from pydantic import ValidationError
from pytest import raises

from app.api.v1.router import api_router
from app.models.table import TableStatus
from app.schemas.tables import TableCreate


def test_table_routes_are_registered() -> None:
    paths = {route.path for route in api_router.routes}

    assert "/tables" in paths
    assert "/tables/floors" in paths
    assert "/tables/{table_id}" in paths


def test_table_create_validates_capacity() -> None:
    with raises(ValidationError):
        TableCreate(table_number="1", floor="Main", capacity=0)


def test_table_create_accepts_valid_status() -> None:
    payload = TableCreate(table_number="1", floor="Main", capacity=4, status=TableStatus.AVAILABLE)

    assert payload.status == TableStatus.AVAILABLE
