import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import type { ReactElement } from "react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";

import { TablesPage } from "../src/features/tables/TablesPage";

const mockUseTables = vi.fn();
const mockUseFloors = vi.fn();
vi.mock("../src/features/tables/hooks", () => ({
  useTables: () => mockUseTables(),
  useFloors: () => mockUseFloors(),
  useCreateTable: () => ({ mutateAsync: vi.fn(), isPending: false }),
  useUpdateTable: () => ({ mutate: vi.fn() }),
  useDeleteTable: () => ({ mutate: vi.fn() })
}));

function renderWithProviders(component: ReactElement) {
  const queryClient = new QueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>{component}</MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("TablesPage", () => {
  it("renders floor and table management data", () => {
    mockUseTables.mockReturnValue({ data: [{ id: "table-1", tableNumber: "1", floor: "Main", capacity: 4, status: "available", createdAt: "", updatedAt: "" }] });
    mockUseFloors.mockReturnValue({ data: [{ floor: "Main", tableCount: 1, availableCount: 1, occupiedCount: 0, reservedCount: 0, inactiveCount: 0 }] });
    renderWithProviders(<TablesPage />);
    expect(screen.getByRole("heading", { name: "Floor management" })).toBeInTheDocument();
    expect(screen.getByText("Table 1")).toBeInTheDocument();
    expect(screen.getAllByText("Main").length).toBeGreaterThan(0);
  });

  it("renders add table form labels", () => {
    mockUseTables.mockReturnValue({ data: [] });
    mockUseFloors.mockReturnValue({ data: [] });
    renderWithProviders(<TablesPage />);
    expect(screen.getByRole("button", { name: "Add table" })).toBeInTheDocument();
    expect(screen.getByLabelText("Table number")).toBeInTheDocument();
    expect(screen.getByLabelText("Floor")).toBeInTheDocument();
    expect(screen.getByLabelText("Capacity")).toBeInTheDocument();
  });
});
