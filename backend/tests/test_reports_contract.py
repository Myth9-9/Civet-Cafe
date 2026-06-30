from datetime import date
from decimal import Decimal

from app.api.v1.router import api_router
from app.models.billing import PaymentMethod
from app.schemas.reports import PaymentMethodTotal, SalesReportResponse


def test_report_routes_are_registered() -> None:
    paths = {route.path for route in api_router.routes}

    assert "/reports/daily" in paths
    assert "/reports/monthly" in paths


def test_sales_report_schema_accepts_aggregate_values() -> None:
    report = SalesReportResponse(
        period_start=date(2026, 6, 1),
        period_end=date(2026, 6, 30),
        bill_count=10,
        paid_bill_count=9,
        gross_sales=Decimal("1000.00"),
        net_sales=Decimal("900.00"),
        tax_collected=Decimal("100.00"),
        discounts=Decimal("0.00"),
        payments_collected=Decimal("1000.00"),
        average_bill_value=Decimal("111.11"),
        payment_methods=[PaymentMethodTotal(method=PaymentMethod.CASH, amount=Decimal("500.00"))],
    )

    assert report.payment_methods[0].method == PaymentMethod.CASH
