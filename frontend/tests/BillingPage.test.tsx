import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";

import { BillingPage } from "../src/features/billing/BillingPage";

vi.mock("../src/features/orders/hooks", () => ({
  useOrders: () => ({
    data: [
      {
        id: "order-1",
        orderNumber: "ORD-20260630-0001",
        status: "served",
        totalAmount: "126.00"
      }
    ]
  })
}));

vi.mock("../src/features/billing/hooks", () => ({
  useBills: () => ({
    data: [
      {
        id: "bill-1",
        billNumber: "BILL-20260630-0001",
        orderId: "order-1",
        issuedByUserId: "user-1",
        status: "issued",
        gstin: null,
        customerName: null,
        customerPhone: null,
        subtotalAmount: "120.00",
        taxAmount: "6.00",
        discountAmount: "0.00",
        totalAmount: "126.00",
        roundedTotalAmount: "126.00",
        payments: []
      }
    ]
  }),
  useReceipt: () => ({
    data: {
      bill: {
        billNumber: "BILL-20260630-0001",
        subtotalAmount: "120.00",
        taxAmount: "6.00",
        roundedTotalAmount: "126.00"
      },
      orderNumber: "ORD-20260630-0001",
      tableId: null,
      paidAmount: "0.00",
      balanceDue: "126.00",
      lines: [{ name: "Espresso", quantity: 1, lineTotal: "126.00" }]
    }
  }),
  useGenerateBill: () => ({ mutate: vi.fn() }),
  useAddPayment: () => ({ mutateAsync: vi.fn() })
}));

describe("BillingPage", () => {
  it("renders billing controls and receipt data", () => {
    const queryClient = new QueryClient();

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <BillingPage />
        </MemoryRouter>
      </QueryClientProvider>,
    );

    expect(screen.getByRole("heading", { name: "Bills & receipts" })).toBeInTheDocument();
    expect(screen.getAllByText("BILL-20260630-0001").length).toBeGreaterThan(0);
    expect(screen.getByText("1 x Espresso")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Save payment" })).toBeInTheDocument();
  });
});
