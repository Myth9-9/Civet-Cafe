import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.db.session import get_db_session
from app.models.order import OrderStatus
from app.schemas.auth import CurrentUserPrincipal
from app.schemas.orders import (
    AddOrderItemRequest,
    OrderCreate,
    OrderResponse,
    OrderStatusUpdate,
    UpdateOrderItemRequest,
)
from app.services.orders import OrderNotFoundError, OrderService, OrderValidationError

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get(
    "",
    response_model=list[OrderResponse],
    dependencies=[Depends(require_permission("orders.read"))],
)
def list_orders(
    order_status: OrderStatus | None = Query(default=None, alias="status"),
    table_id: uuid.UUID | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db_session),
) -> list[OrderResponse]:
    return OrderService(db).list(status=order_status, table_id=table_id, limit=limit, offset=offset)


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    dependencies=[Depends(require_permission("orders.read"))],
)
def get_order(order_id: uuid.UUID, db: Session = Depends(get_db_session)) -> OrderResponse:
    try:
        return OrderService(db).get(order_id)
    except OrderNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    payload: OrderCreate,
    principal: CurrentUserPrincipal = Depends(require_permission("orders.manage")),
    db: Session = Depends(get_db_session),
) -> OrderResponse:
    try:
        return OrderService(db).create(payload=payload, created_by_user_id=principal.user_id)
    except OrderValidationError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/{order_id}/items", response_model=OrderResponse)
def add_order_item(
    order_id: uuid.UUID,
    payload: AddOrderItemRequest,
    _: CurrentUserPrincipal = Depends(require_permission("orders.manage")),
    db: Session = Depends(get_db_session),
) -> OrderResponse:
    try:
        return OrderService(db).add_item(order_id, payload)
    except OrderNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except OrderValidationError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.patch("/{order_id}/items/{item_id}", response_model=OrderResponse)
def update_order_item(
    order_id: uuid.UUID,
    item_id: uuid.UUID,
    payload: UpdateOrderItemRequest,
    _: CurrentUserPrincipal = Depends(require_permission("orders.manage")),
    db: Session = Depends(get_db_session),
) -> OrderResponse:
    try:
        return OrderService(db).update_item(order_id=order_id, item_id=item_id, payload=payload)
    except OrderNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except OrderValidationError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.delete("/{order_id}/items/{item_id}", response_model=OrderResponse)
def remove_order_item(
    order_id: uuid.UUID,
    item_id: uuid.UUID,
    _: CurrentUserPrincipal = Depends(require_permission("orders.manage")),
    db: Session = Depends(get_db_session),
) -> OrderResponse:
    try:
        return OrderService(db).remove_item(order_id=order_id, item_id=item_id)
    except OrderNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except OrderValidationError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/{order_id}/transition", response_model=OrderResponse)
def transition_order(
    order_id: uuid.UUID,
    payload: OrderStatusUpdate,
    _: CurrentUserPrincipal = Depends(require_permission("orders.manage")),
    db: Session = Depends(get_db_session),
) -> OrderResponse:
    try:
        return OrderService(db).transition(order_id, payload.status)
    except OrderNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except OrderValidationError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

