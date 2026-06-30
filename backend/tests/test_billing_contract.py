from decimal import Decimal
from uuid import UUID

from pydantic import ValidationError
from pytest import raises

from app.api.v1.router import api_router
from app.models.billing import PaymentMethod
from app.schemas.billing import BillGenerateRequest, PaymentCreateRequest


def test_billing_routes_are_registered() -> None:
    paths = {route.path for route in api_router.routes}

    assert "/billing/bills" in paths
    assert "/billing/generate" in paths
    assert "/billing/bills/{bill_id}" in paths
    assert "/billing/bills/{bill_id}/payments" in paths
    assert "/billing/bills/{bill_id}/receipt" in paths


def test_bill_generate_requires_order_id() -> None:
    payload = BillGenerateRequest(order_id=UUID("00000000-0000-0000-0000-000000000001"))

    assert str(payload.order_id) == "00000000-0000-0000-0000-000000000001"


def test_payment_requires_positive_amount() -> None:
    with raises(ValidationError):
        PaymentCreateRequest(method=PaymentMethod.CASH, amount=Decimal("0.00"))
