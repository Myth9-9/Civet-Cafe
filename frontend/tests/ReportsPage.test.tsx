import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";

import { ReportsPage } from "../src/features/reports/ReportsPage";

const report = {
  periodStart: "2026-06-30",
  periodEnd: "2026-06-30",
  billCount: 4,
  paidBillCount: 3,
  grossSales: "1500.00",
  netSales: "1428.57",
  taxCollected: "71.43",
  discounts: "0.00",
  paymentsCollected: "1500.00",
  averageBillValue: "500.00",
  paymentMethods: [{ method: "cash", amount: "800.00" }]
};

vi.mock("../src/features/reports/hooks", () => ({
  useDailyReport: () => ({ data: report }),
  useMonthlyReport: () => ({ data: report })
}));

describe("ReportsPage", () => {
  it("renders daily and monthly sales aggregates", () => {
    const queryClient = new QueryClient();

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <ReportsPage />
        </MemoryRouter>
      </QueryClientProvider>,
    );

    expect(screen.getByRole("heading", { name: "Sales reports" })).toBeInTheDocument();
    expect(screen.getByText("3 paid bills from 4 total bills")).toBeInTheDocument();
    expect(screen.getAllByText("INR 1500.00").length).toBeGreaterThan(0);
    expect(screen.getByText("cash")).toBeInTheDocument();
  });
});
