from decimal import Decimal
from uuid import uuid4

from pydantic import ValidationError
from pytest import raises

from app.api.v1.router import api_router
from app.schemas.menu import CategoryCreate, MenuItemCreate


def test_menu_routes_are_registered() -> None:
    paths = {route.path for route in api_router.routes}

    assert "/menu/categories" in paths
    assert "/menu/categories/{category_id}" in paths
    assert "/menu/items" in paths
    assert "/menu/items/{item_id}" in paths


def test_category_create_requires_meaningful_name() -> None:
    with raises(ValidationError):
        CategoryCreate(name="A")


def test_menu_item_create_validates_price_and_tax_rate() -> None:
    with raises(ValidationError):
        MenuItemCreate(
            category_id=uuid4(),
            sku="ESP",
            name="Espresso",
            price=Decimal("0"),
            tax_rate=Decimal("101"),
        )


def test_menu_item_create_accepts_valid_payload() -> None:
    payload = MenuItemCreate(
        category_id=uuid4(),
        sku="ESP",
        name="Espresso",
        price=Decimal("120.00"),
        tax_rate=Decimal("5.00"),
    )

    assert payload.price == Decimal("120.00")

