/**
 * Top header with user profile and logout.
 */

import { LogOut, User } from "lucide-react";
import { useAuth } from "../../hooks/useAuth";

export function Header() {
  const { user, logout } = useAuth();

  return (
    <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-8">
      <div>
        <h2 className="text-lg font-semibold text-gray-800">
          Welcome back, {user?.full_name?.split(" ")[0] || "User"}
        </h2>
      </div>

      <div className="flex items-center gap-4">
        {/* User info */}
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center">
            <User className="w-4 h-4 text-indigo-600" />
          </div>
          <span className="text-sm text-gray-600">{user?.email}</span>
        </div>

        {/* Logout */}
        <button
          onClick={logout}
          className="flex items-center gap-1.5 px-3 py-1.5 text-sm text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all"
        >
          <LogOut className="w-4 h-4" />
          Logout
        </button>
      </div>
    </header>
  );
}
