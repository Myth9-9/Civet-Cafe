import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import type { ReactElement } from "react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";

import { SettingsPage } from "../src/features/admin/SettingsPage";
import { UsersPage } from "../src/features/admin/UsersPage";

vi.mock("../src/features/admin/hooks", () => ({
  useRoles: () => ({ data: [{ id: "role-1", name: "manager", description: null, isSystem: true }] }),
  useUsers: () => ({
    data: [
      {
        id: "user-1",
        supabaseUserId: null,
        roleId: "role-1",
        email: "asha@civetcafe.com",
        fullName: "Asha Rao",
        phone: null,
        employeeCode: "EMP-1",
        isActive: true
      }
    ]
  }),
  useCreateUser: () => ({ mutateAsync: vi.fn() }),
  useUpdateUser: () => ({ mutate: vi.fn() }),
  useDeleteUser: () => ({ mutate: vi.fn() }),
  useSettings: () => ({
    data: [
      {
        id: "setting-1",
        key: "cafe.profile",
        value: { name: "Civet Cafe" },
        isPublic: true
      }
    ]
  }),
  useUpsertSetting: () => ({ mutateAsync: vi.fn() })
}));

function renderWithProviders(component: ReactElement) {
  const queryClient = new QueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>{component}</MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("Admin pages", () => {
  it("renders users management data", () => {
    renderWithProviders(<UsersPage />);

    expect(screen.getByRole("heading", { name: "User management" })).toBeInTheDocument();
    expect(screen.getByText("Asha Rao")).toBeInTheDocument();
    expect(screen.getAllByText("manager").length).toBeGreaterThan(0);
  });

  it("renders settings data", () => {
    renderWithProviders(<SettingsPage />);

    expect(screen.getByRole("heading", { name: "Cafe settings" })).toBeInTheDocument();
    expect(screen.getAllByText("cafe.profile").length).toBeGreaterThan(0);
    expect(screen.getByText(/Civet Cafe/)).toBeInTheDocument();
  });
});
