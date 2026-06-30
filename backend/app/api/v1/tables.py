import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.db.session import get_db_session
from app.schemas.auth import CurrentUserPrincipal
from app.schemas.tables import FloorResponse, TableCreate, TableResponse, TableUpdate
from app.services.tables import TableNotFoundError, TableService, TableValidationError

router = APIRouter(prefix="/tables", tags=["tables"])


@router.get(
    "",
    response_model=list[TableResponse],
    dependencies=[Depends(require_permission("tables.read"))],
)
def list_tables(
    floor: str | None = None,
    include_inactive: bool = False,
    limit: int = Query(default=200, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db_session),
) -> list[TableResponse]:
    return TableService(db).list(
        floor=floor,
        include_inactive=include_inactive,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/floors",
    response_model=list[FloorResponse],
    dependencies=[Depends(require_permission("tables.read"))],
)
def list_floors(db: Session = Depends(get_db_session)) -> list[FloorResponse]:
    return TableService(db).floors()


@router.post("", response_model=TableResponse, status_code=status.HTTP_201_CREATED)
def create_table(
    payload: TableCreate,
    _: CurrentUserPrincipal = Depends(require_permission("tables.manage")),
    db: Session = Depends(get_db_session),
) -> TableResponse:
    try:
        return TableService(db).create(payload)
    except TableValidationError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.patch("/{table_id}", response_model=TableResponse)
def update_table(
    table_id: uuid.UUID,
    payload: TableUpdate,
    _: CurrentUserPrincipal = Depends(require_permission("tables.manage")),
    db: Session = Depends(get_db_session),
) -> TableResponse:
    try:
        return TableService(db).update(table_id, payload)
    except TableNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except TableValidationError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.delete("/{table_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_table(
    table_id: uuid.UUID,
    _: CurrentUserPrincipal = Depends(require_permission("tables.manage")),
    db: Session = Depends(get_db_session),
) -> None:
    try:
        TableService(db).delete(table_id)
    except TableNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except TableValidationError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

