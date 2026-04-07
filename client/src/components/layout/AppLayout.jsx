/**
 * Main app layout — Sidebar + Header + Content area.
 * Used for all authenticated pages.
 */

import { Outlet, Navigate } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { Header } from "./Header";
import { useAuth } from "../../hooks/useAuth";
import { Loader } from "../common/Loader";

export function AppLayout() {
  const { user, loading } = useAuth();

  if (loading) return <Loader text="Loading app..." />;
  if (!user) return <Navigate to="/login" replace />;

  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar />
      <div className="ml-64">
        <Header />
        <main className="p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
