from __future__ import annotations

import uuid
from decimal import Decimal

import pytest

from app.models.billing import BillStatus, PaymentMethod
from app.models.menu import Category, MenuItem
from app.models.order import Order, OrderItem, OrderStatus
from app.models.table import CafeTable, TableStatus
from app.models.user import User
from app.schemas.billing import BillGenerateRequest, PaymentCreateRequest
from app.services.billing import BillingService, BillingValidationError, BillNotFoundError
from app.services.orders import OrderService
from app.schemas.orders import AddOrderItemRequest, OrderCreate


@pytest.fixture
def billing_seed_data(db, seed_rbac):
    """Create a fully served order ready for billing."""
    role = seed_rbac["cashier_role"]
    user = User(
        id=uuid.uuid4(),
        role_id=role.id,
        email="billing-cashier@civetcafe.com",
        full_name="Billing Cashier",
        is_active=True,
    )
    db.add(user)

    table = CafeTable(
        id=uuid.uuid4(),
        table_number="B1",
        floor="Main",
        capacity=4,
        status=TableStatus.AVAILABLE,
    )
    db.add(table)

    category = Category(id=uuid.uuid4(), name="Billing Coffee", display_order=1)
    db.add(category)

    menu_item = MenuItem(
        id=uuid.uuid4(),
        category_id=category.id,
        sku="BCAP-01",
        name="Cappuccino",
        price=Decimal("200.00"),
        tax_rate=Decimal("5.00"),
        is_available=True,
    )
    db.add(menu_item)
    db.commit()

    # Create and progress an order to SERVED
    order_svc = OrderService(db)
    order = order_svc.create(payload=OrderCreate(table_id=table.id), created_by_user_id=user.id)
    order_svc.add_item(order.id, AddOrderItemRequest(menu_item_id=menu_item.id, quantity=2))
    order = order_svc.transition(order.id, OrderStatus.PLACED)
    order = order_svc.transition(order.id, OrderStatus.PREPARING)
    order = order_svc.transition(order.id, OrderStatus.READY)
    order = order_svc.transition(order.id, OrderStatus.SERVED)

    return {"user": user, "table": table, "order": order, "menu_item": menu_item}


def test_generate_bill_from_served_order(db, billing_seed_data):
    user = billing_seed_data["user"]
    order = billing_seed_data["order"]

    service = BillingService(db)
    bill = service.generate(
        payload=BillGenerateRequest(order_id=order.id),
        issued_by_user_id=user.id,
    )

    assert bill.order_id == order.id
    assert bill.status == BillStatus.ISSUED
    # 200 * 2 = 400 subtotal, 400 * 5% = 20 tax, total = 420
    assert bill.subtotal_amount == Decimal("400.00")
    assert bill.tax_amount == Decimal("20.00")
    assert bill.total_amount == Decimal("420.00")
    assert bill.rounded_total_amount == Decimal("420")


def test_generate_bill_rejects_non_served_order(db, seed_rbac):
    role = seed_rbac["cashier_role"]
    user = User(
        id=uuid.uuid4(),
        role_id=role.id,
        email="billing-fail@civetcafe.com",
        full_name="Billing Fail",
        is_active=True,
    )
    db.add(user)

    table = CafeTable(
        id=uuid.uuid4(),
        table_number="BF1",
        floor="Main",
        capacity=2,
        status=TableStatus.AVAILABLE,
    )
    db.add(table)
    db.commit()

    order_svc = OrderService(db)
    order = order_svc.create(payload=OrderCreate(table_id=table.id), created_by_user_id=user.id)

    service = BillingService(db)
    with pytest.raises(BillingValidationError, match="Only served orders can be billed"):
        service.generate(
            payload=BillGenerateRequest(order_id=order.id),
            issued_by_user_id=user.id,
        )


def test_add_payment_and_auto_mark_paid(db, billing_seed_data):
    user = billing_seed_data["user"]
    order = billing_seed_data["order"]

    service = BillingService(db)
    bill = service.generate(
        payload=BillGenerateRequest(order_id=order.id),
        issued_by_user_id=user.id,
    )

    # Partial payment
    bill = service.add_payment(
        bill_id=bill.id,
        payload=PaymentCreateRequest(method=PaymentMethod.CASH, amount=Decimal("200.00")),
    )
    assert bill.status == BillStatus.ISSUED

    # Remaining payment
    bill = service.add_payment(
        bill_id=bill.id,
        payload=PaymentCreateRequest(method=PaymentMethod.UPI, amount=Decimal("220.00")),
    )
    assert bill.status == BillStatus.PAID
    assert len(bill.payments) == 2


def test_payment_exceeding_total_raises_error(db, billing_seed_data):
    user = billing_seed_data["user"]
    order = billing_seed_data["order"]

    service = BillingService(db)
    bill = service.generate(
        payload=BillGenerateRequest(order_id=order.id),
        issued_by_user_id=user.id,
    )

    with pytest.raises(BillingValidationError, match="Payment exceeds bill total"):
        service.add_payment(
            bill_id=bill.id,
            payload=PaymentCreateRequest(method=PaymentMethod.CASH, amount=Decimal("999.00")),
        )


def test_receipt_contains_line_items(db, billing_seed_data):
    user = billing_seed_data["user"]
    order = billing_seed_data["order"]

    service = BillingService(db)
    bill = service.generate(
        payload=BillGenerateRequest(order_id=order.id),
        issued_by_user_id=user.id,
    )

    receipt = service.receipt(bill.id)
    assert receipt.order_number == order.order_number
    assert len(receipt.lines) == 1
    assert receipt.lines[0].name == "Cappuccino"
    assert receipt.lines[0].quantity == 2
    assert receipt.balance_due == bill.rounded_total_amount


def test_void_bill(db, billing_seed_data):
    user = billing_seed_data["user"]
    order = billing_seed_data["order"]

    service = BillingService(db)
    bill = service.generate(
        payload=BillGenerateRequest(order_id=order.id),
        issued_by_user_id=user.id,
    )

    voided = service.void(bill_id=bill.id, reason="Customer cancelled")
    assert voided.status == BillStatus.VOID
    assert voided.void_reason == "Customer cancelled"
    assert voided.voided_at is not None


def test_cannot_generate_bill_for_already_billed_order(db, billing_seed_data):
    user = billing_seed_data["user"]
    order = billing_seed_data["order"]

    service = BillingService(db)
    service.generate(payload=BillGenerateRequest(order_id=order.id), issued_by_user_id=user.id)

    with pytest.raises(BillingValidationError, match="Only served orders can be billed"):
        service.generate(payload=BillGenerateRequest(order_id=order.id), issued_by_user_id=user.id)


def test_cannot_void_already_paid_bill(db, billing_seed_data):
    user = billing_seed_data["user"]
    order = billing_seed_data["order"]

    service = BillingService(db)
    bill = service.generate(payload=BillGenerateRequest(order_id=order.id), issued_by_user_id=user.id)
    service.add_payment(bill_id=bill.id, payload=PaymentCreateRequest(method=PaymentMethod.CASH, amount=bill.rounded_total_amount))

    with pytest.raises(BillingValidationError, match="Paid bills cannot be voided"):
        service.void(bill_id=bill.id, reason="Too late")


def test_generate_bill_with_customer_info(db, billing_seed_data):
    user = billing_seed_data["user"]
    order = billing_seed_data["order"]

    service = BillingService(db)
    bill = service.generate(
        payload=BillGenerateRequest(
            order_id=order.id,
            customer_name="John Doe",
            customer_phone="+919999999999",
            gstin="GSTIN12345",
        ),
        issued_by_user_id=user.id,
    )
    assert bill.customer_name == "John Doe"
    assert bill.customer_phone == "+919999999999"
    assert bill.gstin == "GSTIN12345"


def test_list_bills(db, billing_seed_data):
    user = billing_seed_data["user"]
    order = billing_seed_data["order"]

    service = BillingService(db)
    bill = service.generate(payload=BillGenerateRequest(order_id=order.id), issued_by_user_id=user.id)

    bills = service.list(limit=10, offset=0)
    assert len(bills) >= 1
    assert any(b.id == bill.id for b in bills)


def test_get_bill_by_id(db, billing_seed_data):
    user = billing_seed_data["user"]
    order = billing_seed_data["order"]

    service = BillingService(db)
    bill = service.generate(payload=BillGenerateRequest(order_id=order.id), issued_by_user_id=user.id)

    found = service.get(bill.id)
    assert found.id == bill.id
    assert found.bill_number == bill.bill_number


def test_get_bill_not_found_raises_error(db):
    service = BillingService(db)
    with pytest.raises(BillNotFoundError):
        service.get(uuid.uuid4())


def test_cannot_add_payment_to_voided_bill(db, billing_seed_data):
    user = billing_seed_data["user"]
    order = billing_seed_data["order"]

    service = BillingService(db)
    bill = service.generate(payload=BillGenerateRequest(order_id=order.id), issued_by_user_id=user.id)
    service.void(bill_id=bill.id, reason="Cancelled")

    with pytest.raises(BillingValidationError, match="Cannot pay a void bill"):
        service.add_payment(bill_id=bill.id, payload=PaymentCreateRequest(method=PaymentMethod.CASH, amount=Decimal("100.00")))


def test_receipt_with_balance_due(db, billing_seed_data):
    user = billing_seed_data["user"]
    order = billing_seed_data["order"]

    service = BillingService(db)
    bill = service.generate(payload=BillGenerateRequest(order_id=order.id), issued_by_user_id=user.id)
    service.add_payment(bill_id=bill.id, payload=PaymentCreateRequest(method=PaymentMethod.CASH, amount=Decimal("200.00")))

    receipt = service.receipt(bill.id)
    assert receipt.balance_due > Decimal("0.00")


def test_void_bill_not_found_raises_error(db):
    service = BillingService(db)
    with pytest.raises(BillNotFoundError):
        service.void(bill_id=uuid.uuid4(), reason="Nope")
