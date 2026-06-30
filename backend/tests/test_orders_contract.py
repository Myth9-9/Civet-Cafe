from uuid import UUID

from pydantic import ValidationError
from pytest import raises

from app.api.v1.router import api_router
from app.models.order import OrderStatus
from app.schemas.orders import OrderItemCreate, OrderStatusUpdate


def test_order_routes_are_registered() -> None:
    paths = {route.path for route in api_router.routes}

    assert "/orders" in paths
    assert "/orders/{order_id}" in paths
    assert "/orders/{order_id}/items" in paths
    assert "/orders/{order_id}/items/{item_id}" in paths
    assert "/orders/{order_id}/transition" in paths


def test_order_item_requires_positive_quantity() -> None:
    with raises(ValidationError):
        OrderItemCreate(
            menu_item_id=UUID("00000000-0000-0000-0000-000000000001"),
            quantity=0,
        )


def test_order_status_update_accepts_lifecycle_status() -> None:
    payload = OrderStatusUpdate(status=OrderStatus.PLACED)

    assert payload.status == OrderStatus.PLACED
