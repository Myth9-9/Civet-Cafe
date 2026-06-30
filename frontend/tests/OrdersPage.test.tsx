import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";

import { OrdersPage } from "../src/features/orders/OrdersPage";

vi.mock("../src/features/orders/hooks", () => ({
  useOrders: () => ({
    data: [
      {
        id: "order-1",
        orderNumber: "ORD-20260629-0001",
        tableId: "table-1",
        createdByUserId: "user-1",
        status: "draft",
        subtotalAmount: "120.00",
        taxAmount: "6.00",
        discountAmount: "0.00",
        totalAmount: "126.00",
        notes: null,
        createdAt: "",
        updatedAt: "",
        items: [
          {
            id: "item-1",
            orderId: "order-1",
            menuItemId: "menu-1",
            itemNameSnapshot: "Espresso",
            unitPrice: "120.00",
            taxRate: "5.00",
            quantity: 1,
            lineSubtotal: "120.00",
            lineTax: "6.00",
            lineTotal: "126.00",
            notes: null
          }
        ]
      }
    ]
  }),
  useCreateOrder: () => ({ mutateAsync: vi.fn() }),
  useAddOrderItem: () => ({ mutateAsync: vi.fn() }),
  useTransitionOrder: () => ({ mutate: vi.fn() })
}));

vi.mock("../src/features/tables/hooks", () => ({
  useTables: () => ({
    data: [
      {
        id: "table-1",
        tableNumber: "1",
        floor: "Main",
        capacity: 4,
        status: "occupied",
        createdAt: "",
        updatedAt: ""
      }
    ]
  })
}));

vi.mock("../src/features/menu/hooks", () => ({
  useMenuItems: () => ({
    data: [
      {
        id: "menu-1",
        categoryId: "category-1",
        sku: "ESP",
        name: "Espresso",
        description: null,
        price: "120.00",
        taxRate: "5.00",
        isAvailable: true,
        displayOrder: 0,
        createdAt: "",
        updatedAt: ""
      }
    ]
  })
}));

describe("OrdersPage", () => {
  it("renders order lifecycle controls and line items", () => {
    const queryClient = new QueryClient();

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <OrdersPage />
        </MemoryRouter>
      </QueryClientProvider>,
    );

    expect(screen.getByRole("heading", { name: "Order management" })).toBeInTheDocument();
    expect(screen.getAllByText("ORD-20260629-0001").length).toBeGreaterThan(0);
    expect(screen.getByText("1 x Espresso")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Mark placed" })).toBeInTheDocument();
  });
});
