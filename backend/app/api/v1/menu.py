import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.db.session import get_db_session
from app.schemas.auth import CurrentUserPrincipal
from app.schemas.menu import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
    MenuItemCreate,
    MenuItemResponse,
    MenuItemUpdate,
)
from app.services.menu import CategoryService, MenuItemService, MenuNotFoundError, MenuValidationError

router = APIRouter(prefix="/menu", tags=["menu"])


@router.get(
    "/categories",
    response_model=list[CategoryResponse],
    dependencies=[Depends(require_permission("menu.read"))],
)
def list_categories(
    include_inactive: bool = False,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db_session),
) -> list[CategoryResponse]:
    return CategoryService(db).list(
        include_inactive=include_inactive,
        limit=limit,
        offset=offset,
    )


@router.post(
    "/categories",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_category(
    payload: CategoryCreate,
    _: CurrentUserPrincipal = Depends(require_permission("menu.manage")),
    db: Session = Depends(get_db_session),
) -> CategoryResponse:
    try:
        return CategoryService(db).create(payload)
    except MenuValidationError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.patch(
    "/categories/{category_id}",
    response_model=CategoryResponse,
)
def update_category(
    category_id: uuid.UUID,
    payload: CategoryUpdate,
    _: CurrentUserPrincipal = Depends(require_permission("menu.manage")),
    db: Session = Depends(get_db_session),
) -> CategoryResponse:
    try:
        return CategoryService(db).update(category_id, payload)
    except MenuNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except MenuValidationError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.delete(
    "/categories/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_category(
    category_id: uuid.UUID,
    _: CurrentUserPrincipal = Depends(require_permission("menu.manage")),
    db: Session = Depends(get_db_session),
) -> None:
    try:
        CategoryService(db).delete(category_id)
    except MenuNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get(
    "/items",
    response_model=list[MenuItemResponse],
    dependencies=[Depends(require_permission("menu.read"))],
)
def list_menu_items(
    category_id: uuid.UUID | None = None,
    include_unavailable: bool = False,
    limit: int = Query(default=200, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db_session),
) -> list[MenuItemResponse]:
    return MenuItemService(db).list(
        category_id=category_id,
        include_unavailable=include_unavailable,
        limit=limit,
        offset=offset,
    )


@router.post(
    "/items",
    response_model=MenuItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_menu_item(
    payload: MenuItemCreate,
    _: CurrentUserPrincipal = Depends(require_permission("menu.manage")),
    db: Session = Depends(get_db_session),
) -> MenuItemResponse:
    try:
        return MenuItemService(db).create(payload)
    except MenuValidationError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.patch(
    "/items/{item_id}",
    response_model=MenuItemResponse,
)
def update_menu_item(
    item_id: uuid.UUID,
    payload: MenuItemUpdate,
    _: CurrentUserPrincipal = Depends(require_permission("menu.manage")),
    db: Session = Depends(get_db_session),
) -> MenuItemResponse:
    try:
        return MenuItemService(db).update(item_id, payload)
    except MenuNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except MenuValidationError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_menu_item(
    item_id: uuid.UUID,
    _: CurrentUserPrincipal = Depends(require_permission("menu.manage")),
    db: Session = Depends(get_db_session),
) -> None:
    try:
        MenuItemService(db).delete(item_id)
    except MenuNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

