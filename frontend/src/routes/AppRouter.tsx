import { Route, Routes } from "react-router-dom";

import { AppShell } from "../components/layout/AppShell";
import { SettingsPage } from "../features/admin/SettingsPage";
import { UsersPage } from "../features/admin/UsersPage";
import { LoginPage } from "../features/auth/LoginPage";
import { useAuth } from "../features/auth/useAuth";
import { BillingPage } from "../features/billing/BillingPage";
import { MenuPage } from "../features/menu/MenuPage";
import { OrdersPage } from "../features/orders/OrdersPage";
import { ReportsPage } from "../features/reports/ReportsPage";
import { TablesPage } from "../features/tables/TablesPage";

export function AppRouter() {
  const { isAuthenticated } = useAuth();

  return (
    <Routes>
      <Route path="/" element={isAuthenticated ? <AppShell /> : <LoginPage />} />
      <Route path="/billing" element={isAuthenticated ? <BillingPage /> : <LoginPage />} />
      <Route path="/menu" element={isAuthenticated ? <MenuPage /> : <LoginPage />} />
      <Route path="/orders" element={isAuthenticated ? <OrdersPage /> : <LoginPage />} />
      <Route path="/reports" element={isAuthenticated ? <ReportsPage /> : <LoginPage />} />
      <Route path="/settings" element={isAuthenticated ? <SettingsPage /> : <LoginPage />} />
      <Route path="/tables" element={isAuthenticated ? <TablesPage /> : <LoginPage />} />
      <Route path="/users" element={isAuthenticated ? <UsersPage /> : <LoginPage />} />
    </Routes>
  );
}
