from datetime import UTC, date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.db.session import get_db_session
from app.schemas.reports import SalesReportResponse
from app.services.reports import ReportsService, ReportsValidationError

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get(
    "/daily",
    response_model=SalesReportResponse,
    dependencies=[Depends(require_permission("reports.read"))],
)
def daily_report(
    report_date: date = Query(default_factory=lambda: datetime.now(UTC).date()),
    db: Session = Depends(get_db_session),
) -> SalesReportResponse:
    return ReportsService(db).daily(report_date)


@router.get(
    "/monthly",
    response_model=SalesReportResponse,
    dependencies=[Depends(require_permission("reports.read"))],
)
def monthly_report(
    year: int = Query(ge=2000, le=2100),
    month: int = Query(ge=1, le=12),
    db: Session = Depends(get_db_session),
) -> SalesReportResponse:
    try:
        return ReportsService(db).monthly(year=year, month=month)
    except ReportsValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

