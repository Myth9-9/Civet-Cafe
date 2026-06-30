import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";

import { AppShell } from "../src/components/layout/AppShell";

vi.mock("../src/features/auth/useAuth", () => ({
  useAuth: () => ({
    user: {
      fullName: "Asha Rao",
      roleName: "manager"
    },
    logout: vi.fn()
  })
}));

describe("AppShell", () => {
  it("renders the application identity", () => {
    render(
      <MemoryRouter>
        <AppShell />
      </MemoryRouter>,
    );

    expect(screen.getByText("Civet Cafe")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "POS & Billing System" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Welcome, Asha Rao" })).toBeInTheDocument();
  });
});
