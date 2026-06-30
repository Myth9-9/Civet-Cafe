import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.db.session import get_db_session
from app.schemas.auth import CurrentUserPrincipal
from app.schemas.settings import SettingResponse, SettingUpdate, SettingUpsert
from app.schemas.users import PermissionResponse, RoleResponse, UserCreate, UserResponse, UserUpdate
from app.services.admin import AdminNotFoundError, AdminValidationError, SettingsService, UserAdminService

router = APIRouter(tags=["admin"])


@router.get(
    "/users",
    response_model=list[UserResponse],
    dependencies=[Depends(require_permission("users.read"))],
)
def list_users(
    include_inactive: bool = False,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db_session),
) -> list[UserResponse]:
    return UserAdminService(db).list_users(include_inactive=include_inactive, limit=limit, offset=offset)


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    _: CurrentUserPrincipal = Depends(require_permission("users.manage")),
    db: Session = Depends(get_db_session),
) -> UserResponse:
    try:
        return UserAdminService(db).create_user(payload)
    except AdminValidationError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.patch("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: uuid.UUID,
    payload: UserUpdate,
    _: CurrentUserPrincipal = Depends(require_permission("users.manage")),
    db: Session = Depends(get_db_session),
) -> UserResponse:
    try:
        return UserAdminService(db).update_user(user_id, payload)
    except AdminNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except AdminValidationError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: uuid.UUID,
    _: CurrentUserPrincipal = Depends(require_permission("users.manage")),
    db: Session = Depends(get_db_session),
) -> None:
    try:
        UserAdminService(db).delete_user(user_id)
    except AdminNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get(
    "/roles",
    response_model=list[RoleResponse],
    dependencies=[Depends(require_permission("users.read"))],
)
def list_roles(db: Session = Depends(get_db_session)) -> list[RoleResponse]:
    return UserAdminService(db).list_roles()


@router.get(
    "/permissions",
    response_model=list[PermissionResponse],
    dependencies=[Depends(require_permission("users.read"))],
)
def list_permissions(db: Session = Depends(get_db_session)) -> list[PermissionResponse]:
    return UserAdminService(db).list_permissions()


@router.get(
    "/settings",
    response_model=list[SettingResponse],
    dependencies=[Depends(require_permission("settings.read"))],
)
def list_settings(
    public_only: bool = False,
    db: Session = Depends(get_db_session),
) -> list[SettingResponse]:
    return SettingsService(db).list(public_only=public_only)


@router.put("/settings", response_model=SettingResponse)
def upsert_setting(
    payload: SettingUpsert,
    _: CurrentUserPrincipal = Depends(require_permission("settings.manage")),
    db: Session = Depends(get_db_session),
) -> SettingResponse:
    return SettingsService(db).upsert(payload)


@router.patch("/settings/{key}", response_model=SettingResponse)
def update_setting(
    key: str,
    payload: SettingUpdate,
    _: CurrentUserPrincipal = Depends(require_permission("settings.manage")),
    db: Session = Depends(get_db_session),
) -> SettingResponse:
    try:
        return SettingsService(db).update(key, payload)
    except AdminNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

