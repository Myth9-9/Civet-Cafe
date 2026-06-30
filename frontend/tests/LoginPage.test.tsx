import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { LoginPage } from "../src/features/auth/LoginPage";

const mockUseAuth = vi.fn();
vi.mock("../src/features/auth/useAuth", () => ({
  useAuth: () => mockUseAuth()
}));

describe("LoginPage", () => {
  it("renders the staff login form", () => {
    mockUseAuth.mockReturnValue({ login: vi.fn(), isLoggingIn: false });
    render(<LoginPage />);

    expect(screen.getByRole("heading", { name: "Open register" })).toBeInTheDocument();
    expect(screen.getByLabelText("Email")).toBeInTheDocument();
    expect(screen.getByLabelText("Password")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Sign in" })).toBeInTheDocument();
  });

  it("shows 'Signing in' and disables button while logging in", () => {
    mockUseAuth.mockReturnValue({ login: vi.fn(), isLoggingIn: true });
    render(<LoginPage />);
    expect(screen.getByRole("button", { name: "Signing in" })).toBeDisabled();
  });
});
