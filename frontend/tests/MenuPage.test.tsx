import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import type { ReactElement } from "react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";

import { MenuPage } from "../src/features/menu/MenuPage";

const mockUseCategories = vi.fn();
const mockUseMenuItems = vi.fn();
vi.mock("../src/features/menu/hooks", () => ({
  useCategories: () => mockUseCategories(),
  useMenuItems: () => mockUseMenuItems(),
  useCreateCategory: () => ({ mutateAsync: vi.fn(), isPending: false }),
  useUpdateCategory: () => ({ mutate: vi.fn() }),
  useDeleteCategory: () => ({ mutate: vi.fn() }),
  useCreateMenuItem: () => ({ mutateAsync: vi.fn(), isPending: false }),
  useUpdateMenuItem: () => ({ mutate: vi.fn() }),
  useDeleteMenuItem: () => ({ mutate: vi.fn() })
}));

function renderWithProviders(component: ReactElement) {
  const queryClient = new QueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>{component}</MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("MenuPage", () => {
  it("renders categories and items", () => {
    mockUseCategories.mockReturnValue({ data: [{ id: "category-1", name: "Coffee", description: null, displayOrder: 0, isActive: true, createdAt: "", updatedAt: "" }] });
    mockUseMenuItems.mockReturnValue({ data: [{ id: "item-1", categoryId: "category-1", sku: "ESP", name: "Espresso", description: null, price: "120.00", taxRate: "5.00", isAvailable: true, displayOrder: 0, createdAt: "", updatedAt: "" }] });
    renderWithProviders(<MenuPage />);
    expect(screen.getByRole("heading", { name: "Menu management" })).toBeInTheDocument();
    expect(screen.getAllByText("Coffee").length).toBeGreaterThan(0);
    expect(screen.getByText("Espresso")).toBeInTheDocument();
  });

  it("renders add category form", () => {
    mockUseCategories.mockReturnValue({ data: [] });
    mockUseMenuItems.mockReturnValue({ data: [] });
    renderWithProviders(<MenuPage />);
    expect(screen.getByRole("button", { name: "Add category" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Add item" })).toBeInTheDocument();
    expect(screen.getByLabelText("Category name")).toBeInTheDocument();
  });
});
