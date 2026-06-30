from __future__ import annotations

import uuid
from decimal import Decimal
import pytest

from app.models.menu import Category, MenuItem
from app.models.table import CafeTable, TableStatus
from app.models.order import Order, OrderItem, OrderStatus
from app.models.user import User
from app.services.orders import OrderService, OrderValidationError, OrderNotFoundError
from app.schemas.orders import OrderCreate, AddOrderItemRequest, UpdateOrderItemRequest


@pytest.fixture
def order_seed_data(db, seed_rbac):
    role = seed_rbac["cashier_role"]
    user = User(
        id=uuid.uuid4(),
        role_id=role.id,
        email="waiter@civetcafe.com",
        full_name="Waiter Bob",
        is_active=True,
    )
    db.add(user)

    table = CafeTable(
        id=uuid.uuid4(),
        table_number="T10",
        floor="Main Floor",
        capacity=4,
        status=TableStatus.AVAILABLE,
    )
    db.add(table)

    category = Category(
        id=uuid.uuid4(),
        name="Desserts",
        display_order=1,
    )
    db.add(category)

    menu_item = MenuItem(
        id=uuid.uuid4(),
        category_id=category.id,
        sku="CAKE-01",
        name="Chocolate Cake",
        price=Decimal("150.00"),
        tax_rate=Decimal("10.00"),
        is_available=True,
    )
    db.add(menu_item)
    db.commit()

    return {
        "user": user,
        "table": table,
        "menu_item": menu_item,
    }


def test_create_order_succeeds(db, order_seed_data):
    user = order_seed_data["user"]
    table = order_seed_data["table"]

    service = OrderService(db)
    payload = OrderCreate(
        table_id=table.id,
        notes="Allergies: Nuts",
    )
    order = service.create(payload=payload, created_by_user_id=user.id)

    assert order.table_id == table.id
    assert order.created_by_user_id == user.id
    assert order.status == OrderStatus.DRAFT
    assert order.notes == "Allergies: Nuts"
    assert order.total_amount == Decimal("0.00")
    
    # Check table status is now OCCUPIED
    assert table.status == TableStatus.OCCUPIED


def test_add_item_to_order_recalculates_totals(db, order_seed_data):
    user = order_seed_data["user"]
    table = order_seed_data["table"]
    menu_item = order_seed_data["menu_item"]

    service = OrderService(db)
    order = service.create(payload=OrderCreate(table_id=table.id), created_by_user_id=user.id)

    # Add item
    payload = AddOrderItemRequest(menu_item_id=menu_item.id, quantity=2, notes="Extra whipped cream")
    updated_order = service.add_item(order.id, payload)

    assert len(updated_order.items) == 1
    item = updated_order.items[0]
    assert item.menu_item_id == menu_item.id
    assert item.quantity == 2
    assert item.unit_price == Decimal("150.00")
    
    # Subtotal: 150 * 2 = 300
    # Tax: 300 * 10% = 30
    # Total: 330
    assert updated_order.subtotal_amount == Decimal("300.00")
    assert updated_order.tax_amount == Decimal("30.00")
    assert updated_order.total_amount == Decimal("330.00")


def test_update_item_quantity(db, order_seed_data):
    user = order_seed_data["user"]
    table = order_seed_data["table"]
    menu_item = order_seed_data["menu_item"]

    service = OrderService(db)
    order = service.create(payload=OrderCreate(table_id=table.id), created_by_user_id=user.id)
    service.add_item(order.id, AddOrderItemRequest(menu_item_id=menu_item.id, quantity=1))
    
    item_id = order.items[0].id
    
    # Update quantity to 3
    payload = UpdateOrderItemRequest(quantity=3)
    updated_order = service.update_item(
        order_id=order.id,
        item_id=item_id,
        payload=payload,
    )
    
    assert updated_order.items[0].quantity == 3
    # Subtotal: 150 * 3 = 450
    # Tax: 450 * 10% = 45
    # Total: 495
    assert updated_order.subtotal_amount == Decimal("450.00")
    assert updated_order.tax_amount == Decimal("45.00")
    assert updated_order.total_amount == Decimal("495.00")


def test_remove_item_from_order(db, order_seed_data):
    user = order_seed_data["user"]
    table = order_seed_data["table"]
    menu_item = order_seed_data["menu_item"]

    service = OrderService(db)
    order = service.create(payload=OrderCreate(table_id=table.id), created_by_user_id=user.id)
    service.add_item(order.id, AddOrderItemRequest(menu_item_id=menu_item.id, quantity=1))
    
    item_id = order.items[0].id
    
    # Remove item
    updated_order = service.remove_item(
        order_id=order.id,
        item_id=item_id,
    )
    assert len(updated_order.items) == 0
    assert updated_order.total_amount == Decimal("0.00")


def test_order_status_transitions(db, order_seed_data):
    user = order_seed_data["user"]
    table = order_seed_data["table"]
    menu_item = order_seed_data["menu_item"]

    service = OrderService(db)
    order = service.create(payload=OrderCreate(table_id=table.id), created_by_user_id=user.id)
    service.add_item(order.id, AddOrderItemRequest(menu_item_id=menu_item.id, quantity=1))

    # DRAFT -> PLACED
    order = service.transition(order.id, OrderStatus.PLACED)
    assert order.status == OrderStatus.PLACED

    # PLACED -> PREPARING
    order = service.transition(order.id, OrderStatus.PREPARING)
    assert order.status == OrderStatus.PREPARING

    # PREPARING -> READY
    order = service.transition(order.id, OrderStatus.READY)
    assert order.status == OrderStatus.READY

    # READY -> SERVED
    order = service.transition(order.id, OrderStatus.SERVED)
    assert order.status == OrderStatus.SERVED


def test_invalid_status_transition_raises_error(db, order_seed_data):
    user = order_seed_data["user"]
    table = order_seed_data["table"]

    service = OrderService(db)
    order = service.create(payload=OrderCreate(table_id=table.id), created_by_user_id=user.id)

    # DRAFT directly to READY is illegal
    with pytest.raises(OrderValidationError) as exc_info:
        service.transition(order.id, OrderStatus.READY)
    assert "Cannot transition order from OrderStatus.DRAFT to OrderStatus.READY" in str(exc_info.value)


def test_cannot_place_order_without_items(db, order_seed_data):
    user = order_seed_data["user"]
    table = order_seed_data["table"]

    service = OrderService(db)
    order = service.create(payload=OrderCreate(table_id=table.id), created_by_user_id=user.id)

    with pytest.raises(OrderValidationError, match="Cannot place an order without items"):
        service.transition(order.id, OrderStatus.PLACED)


def test_cannot_edit_order_after_served(db, order_seed_data):
    user = order_seed_data["user"]
    table = order_seed_data["table"]
    menu_item = order_seed_data["menu_item"]

    service = OrderService(db)
    order = service.create(payload=OrderCreate(table_id=table.id), created_by_user_id=user.id)
    service.add_item(order.id, AddOrderItemRequest(menu_item_id=menu_item.id, quantity=1))
    service.transition(order.id, OrderStatus.PLACED)
    service.transition(order.id, OrderStatus.PREPARING)
    service.transition(order.id, OrderStatus.READY)
    service.transition(order.id, OrderStatus.SERVED)

    with pytest.raises(OrderValidationError, match="Order can no longer be edited"):
        service.add_item(order.id, AddOrderItemRequest(menu_item_id=menu_item.id, quantity=1))


def test_cannot_add_unavailable_menu_item(db, order_seed_data):
    user = order_seed_data["user"]
    table = order_seed_data["table"]

    # Create unavailable menu item
    bad_item = MenuItem(
        id=uuid.uuid4(),
        category_id=order_seed_data["menu_item"].category_id,
        sku="UNAVAIL-01",
        name="Not Available",
        price=Decimal("100.00"),
        tax_rate=Decimal("5.00"),
        is_available=False,
    )
    db.add(bad_item)
    db.commit()

    service = OrderService(db)
    order = service.create(payload=OrderCreate(table_id=table.id), created_by_user_id=user.id)

    with pytest.raises(OrderValidationError, match="Menu item is not available"):
        service.add_item(order.id, AddOrderItemRequest(menu_item_id=bad_item.id, quantity=1))


def test_cannot_create_order_on_occupied_table(db, order_seed_data):
    user = order_seed_data["user"]
    table = order_seed_data["table"]
    menu_item = order_seed_data["menu_item"]

    # First order occupies the table
    service = OrderService(db)
    order = service.create(payload=OrderCreate(table_id=table.id), created_by_user_id=user.id)
    service.add_item(order.id, AddOrderItemRequest(menu_item_id=menu_item.id, quantity=1))

    with pytest.raises(OrderValidationError, match="Table is already occupied"):
        service.create(payload=OrderCreate(table_id=table.id), created_by_user_id=user.id)


def test_order_not_found_raises_error(db):
    service = OrderService(db)
    with pytest.raises(OrderNotFoundError):
        service.get(uuid.uuid4())


def test_transition_to_billed_frees_table(db, order_seed_data):
    user = order_seed_data["user"]
    table = order_seed_data["table"]
    menu_item = order_seed_data["menu_item"]

    service = OrderService(db)
    order = service.create(payload=OrderCreate(table_id=table.id), created_by_user_id=user.id)
    service.add_item(order.id, AddOrderItemRequest(menu_item_id=menu_item.id, quantity=1))
    service.transition(order.id, OrderStatus.PLACED)
    service.transition(order.id, OrderStatus.PREPARING)
    service.transition(order.id, OrderStatus.READY)
    service.transition(order.id, OrderStatus.SERVED)
    service.transition(order.id, OrderStatus.BILLED)

    assert table.status == TableStatus.AVAILABLE


def test_list_orders_with_filters(db, order_seed_data):
    user = order_seed_data["user"]
    table = order_seed_data["table"]
    menu_item = order_seed_data["menu_item"]

    service = OrderService(db)
    order1 = service.create(payload=OrderCreate(table_id=table.id), created_by_user_id=user.id)
    service.add_item(order1.id, AddOrderItemRequest(menu_item_id=menu_item.id, quantity=1))

    svc = OrderService(db)
    placed_orders = svc.list(status=OrderStatus.DRAFT, table_id=None, limit=10, offset=0)
    assert len(placed_orders) >= 1

    cancelled_orders = svc.list(status=OrderStatus.CANCELLED, table_id=None, limit=10, offset=0)
    assert len(cancelled_orders) == 0
