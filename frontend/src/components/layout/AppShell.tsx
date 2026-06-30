import { Coffee, LogOut } from "lucide-react";
import { Link } from "react-router-dom";

import { useAuth } from "../../features/auth/useAuth";

export function AppShell() {
  const { user, logout } = useAuth();

  return (
    <main className="min-h-screen bg-civet-background text-civet-ink">
      <header className="border-b border-civet-outlineVariant bg-civet-surface">
        <div className="mx-auto flex min-h-16 max-w-6xl items-center justify-between px-6">
          <div className="flex items-center gap-3">
            <span className="grid size-11 place-items-center rounded bg-civet-espresso text-white">
              <Coffee aria-hidden="true" size={24} />
            </span>
            <div>
              <p className="text-xs font-semibold uppercase text-civet-muted">Civet Cafe</p>
              <h1 className="font-display text-xl font-semibold">POS & Billing System</h1>
            </div>
          </div>
          <button
            aria-label="Sign out"
            className="grid size-11 place-items-center rounded border border-civet-outlineVariant text-civet-muted hover:border-civet-espresso hover:text-civet-espresso"
            onClick={() => void logout()}
            type="button"
          >
            <LogOut aria-hidden="true" size={20} />
          </button>
        </div>
      </header>
      <section className="mx-auto flex min-h-[calc(100vh-4rem)] max-w-6xl flex-col justify-center px-6">
        <div className="flex items-center gap-3">
          <span className="grid size-11 place-items-center rounded bg-civet-espresso text-white">
            <Coffee aria-hidden="true" size={24} />
          </span>
          <div>
            <p className="text-sm font-semibold uppercase text-civet-muted">
              {user?.roleName ?? "Staff"}
            </p>
            <h2 className="font-display text-3xl font-semibold">
              Welcome{user ? `, ${user.fullName}` : ""}
            </h2>
          </div>
        </div>
        <div className="mt-8 flex flex-wrap gap-3">
          <Link
            className="inline-flex min-h-12 items-center rounded bg-civet-espresso px-4 text-sm font-semibold text-white"
            to="/menu"
          >
            Manage menu
          </Link>
          <Link
            className="inline-flex min-h-12 items-center rounded border border-civet-outlineVariant px-4 text-sm font-semibold text-civet-espresso"
            to="/tables"
          >
            Manage tables
          </Link>
          <Link
            className="inline-flex min-h-12 items-center rounded border border-civet-outlineVariant px-4 text-sm font-semibold text-civet-espresso"
            to="/orders"
          >
            Manage orders
          </Link>
          <Link
            className="inline-flex min-h-12 items-center rounded border border-civet-outlineVariant px-4 text-sm font-semibold text-civet-espresso"
            to="/billing"
          >
            Billing
          </Link>
          <Link
            className="inline-flex min-h-12 items-center rounded border border-civet-outlineVariant px-4 text-sm font-semibold text-civet-espresso"
            to="/reports"
          >
            Reports
          </Link>
          <Link
            className="inline-flex min-h-12 items-center rounded border border-civet-outlineVariant px-4 text-sm font-semibold text-civet-espresso"
            to="/users"
          >
            Users
          </Link>
          <Link
            className="inline-flex min-h-12 items-center rounded border border-civet-outlineVariant px-4 text-sm font-semibold text-civet-espresso"
            to="/settings"
          >
            Settings
          </Link>
        </div>
      </section>
    </main>
  );
}
