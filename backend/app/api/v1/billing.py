import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.db.session import get_db_session
from app.schemas.auth import CurrentUserPrincipal
from app.schemas.billing import (
    BillGenerateRequest,
    BillResponse,
    PaymentCreateRequest,
    ReceiptResponse,
)
from app.services.billing import BillingService, BillingValidationError, BillNotFoundError

router = APIRouter(prefix="/billing", tags=["billing"])


class VoidBillRequest(BaseModel):
    reason: str = Field(min_length=3, max_length=1000)


@router.get(
    "/bills",
    response_model=list[BillResponse],
    dependencies=[Depends(require_permission("billing.read"))],
)
def list_bills(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db_session),
) -> list[BillResponse]:
    return BillingService(db).list(limit=limit, offset=offset)


@router.post("/generate", response_model=BillResponse, status_code=status.HTTP_201_CREATED)
def generate_bill(
    payload: BillGenerateRequest,
    principal: CurrentUserPrincipal = Depends(require_permission("billing.manage")),
    db: Session = Depends(get_db_session),
) -> BillResponse:
    try:
        return BillingService(db).generate(payload=payload, issued_by_user_id=principal.user_id)
    except BillingValidationError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.get(
    "/bills/{bill_id}",
    response_model=BillResponse,
    dependencies=[Depends(require_permission("billing.read"))],
)
def get_bill(bill_id: uuid.UUID, db: Session = Depends(get_db_session)) -> BillResponse:
    try:
        return BillingService(db).get(bill_id)
    except BillNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/bills/{bill_id}/payments", response_model=BillResponse)
def add_payment(
    bill_id: uuid.UUID,
    payload: PaymentCreateRequest,
    _: CurrentUserPrincipal = Depends(require_permission("billing.manage")),
    db: Session = Depends(get_db_session),
) -> BillResponse:
    try:
        return BillingService(db).add_payment(bill_id=bill_id, payload=payload)
    except BillNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except BillingValidationError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.get(
    "/bills/{bill_id}/receipt",
    response_model=ReceiptResponse,
    dependencies=[Depends(require_permission("billing.read"))],
)
def get_receipt(bill_id: uuid.UUID, db: Session = Depends(get_db_session)) -> ReceiptResponse:
    try:
        return BillingService(db).receipt(bill_id)
    except BillNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except BillingValidationError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/bills/{bill_id}/void", response_model=BillResponse)
def void_bill(
    bill_id: uuid.UUID,
    payload: VoidBillRequest,
    _: CurrentUserPrincipal = Depends(require_permission("billing.manage")),
    db: Session = Depends(get_db_session),
) -> BillResponse:
    try:
        return BillingService(db).void(bill_id=bill_id, reason=payload.reason)
    except BillNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except BillingValidationError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

