from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from app.models.billing import Bill, BillStatus, Payment, PaymentMethod, PaymentStatus
from app.models.menu import Category, MenuItem
from app.models.order import Order, OrderItem, OrderStatus
from app.models.table import CafeTable, TableStatus
from app.models.user import User
from app.schemas.orders import AddOrderItemRequest, OrderCreate
from app.services.orders import OrderService
from app.services.reports import ReportsService, ReportsValidationError


def _create_served_order_with_paid_bill(
    db,
    user: User,
    table: CafeTable,
    menu_item: MenuItem,
    *,
    quantity: int = 2,
    days_ago: int = 0,
) -> Bill:
    """Helper to create a served order and a fully paid bill for testing reports."""
    order_svc = OrderService(db)
    order = order_svc.create(payload=OrderCreate(table_id=table.id), created_by_user_id=user.id)
    order_svc.add_item(order.id, AddOrderItemRequest(menu_item_id=menu_item.id, quantity=quantity))
    order = order_svc.transition(order.id, OrderStatus.PLACED)
    order = order_svc.transition(order.id, OrderStatus.PREPARING)
    order = order_svc.transition(order.id, OrderStatus.READY)
    order = order_svc.transition(order.id, OrderStatus.SERVED)

    # Shift created_at into the past if needed
    if days_ago > 0:
        past = datetime.now(UTC) - timedelta(days=days_ago)
        order.created_at = past
        db.flush()

    from app.services.billing import BillingService
    from app.schemas.billing import BillGenerateRequest, PaymentCreateRequest

    bill_svc = BillingService(db)
    bill = bill_svc.generate(payload=BillGenerateRequest(order_id=order.id), issued_by_user_id=user.id)
    bill_svc.add_payment(bill_id=bill.id, payload=PaymentCreateRequest(method=PaymentMethod.CASH, amount=bill.rounded_total_amount))
    db.refresh(bill)
    return bill


@pytest.fixture
def report_seed_data(db, seed_rbac):
    role = seed_rbac["cashier_role"]
    user = User(
        id=uuid.uuid4(),
        role_id=role.id,
        email="report-cashier@civetcafe.com",
        full_name="Report Cashier",
        is_active=True,
    )
    db.add(user)

    table = CafeTable(
        id=uuid.uuid4(),
        table_number="R1",
        floor="Main",
        capacity=4,
        status=TableStatus.AVAILABLE,
    )
    db.add(table)

    category = Category(id=uuid.uuid4(), name="Report Items", display_order=1)
    db.add(category)

    menu_item = MenuItem(
        id=uuid.uuid4(),
        category_id=category.id,
        sku="R-ITEM-01",
        name="Report Coffee",
        price=Decimal("100.00"),
        tax_rate=Decimal("5.00"),
        is_available=True,
    )
    db.add(menu_item)
    db.commit()

    return {"user": user, "table": table, "menu_item": menu_item}


class TestReportsService:
    def test_daily_report_with_data(self, db, report_seed_data):
        data = report_seed_data
        _create_served_order_with_paid_bill(db, data["user"], data["table"], data["menu_item"])

        now = datetime.now(UTC)
        svc = ReportsService(db)
        report = svc.daily(report_date=now.date())

        assert report.bill_count == 1
        assert report.paid_bill_count == 1
        assert report.gross_sales > Decimal("0.00")
        assert report.net_sales > Decimal("0.00")
        assert report.tax_collected > Decimal("0.00")
        assert report.payment_methods[0].method == PaymentMethod.CASH

    def test_daily_report_no_data_returns_zeros(self, db):
        svc = ReportsService(db)
        report = svc.daily(report_date=datetime.now(UTC).date())

        assert report.bill_count == 0
        assert report.paid_bill_count == 0
        assert report.gross_sales == Decimal("0.00")
        assert report.net_sales == Decimal("0.00")
        assert report.tax_collected == Decimal("0.00")
        assert report.payments_collected == Decimal("0.00")
        assert report.average_bill_value == Decimal("0.00")
        assert report.payment_methods == []

    def test_monthly_report_with_data(self, db, report_seed_data):
        data = report_seed_data
        _create_served_order_with_paid_bill(db, data["user"], data["table"], data["menu_item"])

        now = datetime.now(UTC)
        svc = ReportsService(db)
        report = svc.monthly(year=now.year, month=now.month)

        assert report.bill_count >= 1

    def test_monthly_report_filters_out_of_range(self, db):
        svc = ReportsService(db)
        with pytest.raises(ReportsValidationError, match="Month must be between 1 and 12"):
            svc.monthly(year=2026, month=13)

    def test_monthly_report_filters_invalid_year(self, db):
        svc = ReportsService(db)
        with pytest.raises(ReportsValidationError, match="Year is outside supported range"):
            svc.monthly(year=1999, month=1)

    def test_report_counts_only_paid_bills(self, db, report_seed_data):
        data = report_seed_data

        # Create an issued (unpaid) bill
        _create_served_order_with_paid_bill(db, data["user"], data["table"], data["menu_item"], quantity=1)

        # Create a second order but don't pay it
        table2 = CafeTable(
            id=uuid.uuid4(),
            table_number="R2",
            floor="Main",
            capacity=2,
            status=TableStatus.AVAILABLE,
        )
        db.add(table2)
        db.commit()

        order_svc = OrderService(db)
        order2 = order_svc.create(payload=OrderCreate(table_id=table2.id), created_by_user_id=data["user"].id)
        order_svc.add_item(order2.id, AddOrderItemRequest(menu_item_id=data["menu_item"].id, quantity=1))
        order2 = order_svc.transition(order2.id, OrderStatus.PLACED)
        order2 = order_svc.transition(order2.id, OrderStatus.PREPARING)
        order2 = order_svc.transition(order2.id, OrderStatus.READY)
        order2 = order_svc.transition(order2.id, OrderStatus.SERVED)

        from app.services.billing import BillingService
        from app.schemas.billing import BillGenerateRequest

        bill_svc = BillingService(db)
        bill_svc.generate(payload=BillGenerateRequest(order_id=order2.id), issued_by_user_id=data["user"].id)
        # No payment added - bill remains ISSUED

        now = datetime.now(UTC)
        svc = ReportsService(db)
        report = svc.daily(report_date=now.date())

        assert report.bill_count == 2
        assert report.paid_bill_count == 1

    def test_report_average_bill_value(self, db, report_seed_data):
        data = report_seed_data
        _create_served_order_with_paid_bill(db, data["user"], data["table"], data["menu_item"], quantity=2)

        now = datetime.now(UTC)
        svc = ReportsService(db)
        report = svc.daily(report_date=now.date())

        # 2 items at 100 each + 5% tax = 210 total
        # average should equal the only bill's value
        assert report.average_bill_value == report.payments_collected
