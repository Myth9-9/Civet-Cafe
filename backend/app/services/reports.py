from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.orm import Session

from app.models.billing import PaymentMethod
from app.repositories.reports import ReportsRepository
from app.schemas.reports import PaymentMethodTotal, SalesReportResponse


class ReportsValidationError(ValueError):
    pass


class ReportsService:
    def __init__(self, db: Session) -> None:
        self._reports = ReportsRepository(db)

    def daily(self, report_date: date) -> SalesReportResponse:
        start_at = datetime.combine(report_date, time.min, tzinfo=UTC)
        end_at = start_at + timedelta(days=1)
        return self._build_report(period_start=report_date, period_end=report_date, start_at=start_at, end_at=end_at)

    def monthly(self, *, year: int, month: int) -> SalesReportResponse:
        if month < 1 or month > 12:
            raise ReportsValidationError("Month must be between 1 and 12")
        if year < 2000 or year > 2100:
            raise ReportsValidationError("Year is outside supported range")
        period_start = date(year, month, 1)
        if month == 12:
            next_month = date(year + 1, 1, 1)
        else:
            next_month = date(year, month + 1, 1)
        period_end = next_month - timedelta(days=1)
        start_at = datetime.combine(period_start, time.min, tzinfo=UTC)
        end_at = datetime.combine(next_month, time.min, tzinfo=UTC)
        return self._build_report(
            period_start=period_start,
            period_end=period_end,
            start_at=start_at,
            end_at=end_at,
        )

    def _build_report(
        self,
        *,
        period_start: date,
        period_end: date,
        start_at: datetime,
        end_at: datetime,
    ) -> SalesReportResponse:
        bill_count, paid_bill_count, gross_sales, tax_collected, discounts = self._reports.bill_totals(
            start_at=start_at,
            end_at=end_at,
        )
        payments_collected = self._reports.payment_total(start_at=start_at, end_at=end_at)
        method_totals = self._reports.payment_method_totals(start_at=start_at, end_at=end_at)
        net_sales = gross_sales - tax_collected
        average = gross_sales / paid_bill_count if paid_bill_count else Decimal("0.00")
        return SalesReportResponse(
            period_start=period_start,
            period_end=period_end,
            bill_count=bill_count,
            paid_bill_count=paid_bill_count,
            gross_sales=self._money(gross_sales),
            net_sales=self._money(net_sales),
            tax_collected=self._money(tax_collected),
            discounts=self._money(discounts),
            payments_collected=self._money(payments_collected),
            average_bill_value=self._money(average),
            payment_methods=[
                PaymentMethodTotal(method=PaymentMethod(method), amount=self._money(amount))
                for method, amount in method_totals
            ],
        )

    def _money(self, value: Decimal) -> Decimal:
        return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

