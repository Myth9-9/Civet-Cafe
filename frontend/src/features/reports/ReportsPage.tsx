import { ArrowLeft } from "lucide-react";
import { useMemo, useState } from "react";
import { Link } from "react-router-dom";

import { useDailyReport, useMonthlyReport } from "./hooks";
import type { SalesReport } from "./types";

function todayIso(): string {
  return new Date().toISOString().slice(0, 10);
}

function money(value: string): string {
  return `INR ${Number(value).toFixed(2)}`;
}

function ReportCards({ report }: { report: SalesReport | undefined }) {
  const cards = [
    ["Gross sales", report?.grossSales ?? "0.00"],
    ["Net sales", report?.netSales ?? "0.00"],
    ["GST collected", report?.taxCollected ?? "0.00"],
    ["Payments", report?.paymentsCollected ?? "0.00"],
    ["Average bill", report?.averageBillValue ?? "0.00"]
  ];

  return (
    <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-5">
      {cards.map(([label, value]) => (
        <article className="rounded-lg border border-civet-outlineVariant bg-civet-surfaceLow p-4" key={label}>
          <p className="text-xs font-semibold uppercase text-civet-muted">{label}</p>
          <h3 className="mt-2 font-display text-2xl font-semibold">{money(value)}</h3>
        </article>
      ))}
    </div>
  );
}

export function ReportsPage() {
  const now = useMemo(() => new Date(), []);
  const [reportDate, setReportDate] = useState(todayIso());
  const [year, setYear] = useState(now.getFullYear());
  const [month, setMonth] = useState(now.getMonth() + 1);
  const daily = useDailyReport(reportDate);
  const monthly = useMonthlyReport(year, month);

  return (
    <main className="min-h-screen bg-civet-background text-civet-ink">
      <header className="border-b border-civet-outlineVariant bg-civet-surface">
        <div className="mx-auto flex min-h-16 max-w-7xl items-center justify-between px-6">
          <div>
            <p className="text-xs font-semibold uppercase text-civet-muted">Reports</p>
            <h1 className="font-display text-2xl font-semibold">Sales reports</h1>
          </div>
          <Link
            aria-label="Back to dashboard"
            className="grid size-11 place-items-center rounded border border-civet-outlineVariant text-civet-muted"
            to="/"
          >
            <ArrowLeft aria-hidden="true" size={20} />
          </Link>
        </div>
      </header>

      <section className="mx-auto max-w-7xl space-y-6 px-6 py-6">
        <section className="rounded-lg border border-civet-outlineVariant bg-civet-surface p-4">
          <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="text-xs font-semibold uppercase text-civet-muted">Daily</p>
              <h2 className="font-display text-xl font-semibold">Daily sales</h2>
            </div>
            <input
              aria-label="Daily report date"
              className="min-h-11 rounded border border-civet-outlineVariant bg-civet-surfaceLow px-3"
              onChange={(event) => setReportDate(event.target.value)}
              type="date"
              value={reportDate}
            />
          </div>
          <ReportCards report={daily.data} />
          <p className="mt-4 text-sm text-civet-muted">
            {daily.data?.paidBillCount ?? 0} paid bills from {daily.data?.billCount ?? 0} total bills
          </p>
        </section>

        <section className="rounded-lg border border-civet-outlineVariant bg-civet-surface p-4">
          <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="text-xs font-semibold uppercase text-civet-muted">Monthly</p>
              <h2 className="font-display text-xl font-semibold">Monthly sales</h2>
            </div>
            <div className="flex gap-2">
              <input
                aria-label="Report year"
                className="min-h-11 w-28 rounded border border-civet-outlineVariant bg-civet-surfaceLow px-3"
                onChange={(event) => setYear(Number(event.target.value))}
                type="number"
                value={year}
              />
              <input
                aria-label="Report month"
                className="min-h-11 w-24 rounded border border-civet-outlineVariant bg-civet-surfaceLow px-3"
                max={12}
                min={1}
                onChange={(event) => setMonth(Number(event.target.value))}
                type="number"
                value={month}
              />
            </div>
          </div>
          <ReportCards report={monthly.data} />
          <div className="mt-5 grid gap-3 md:grid-cols-3">
            {(monthly.data?.paymentMethods ?? []).map((method) => (
              <article className="rounded border border-civet-outlineVariant bg-civet-surfaceLow p-3" key={method.method}>
                <p className="text-xs font-semibold uppercase text-civet-muted">{method.method}</p>
                <p className="font-display text-xl font-semibold">{money(method.amount)}</p>
              </article>
            ))}
          </div>
        </section>
      </section>
    </main>
  );
}

