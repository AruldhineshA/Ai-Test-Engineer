/**
 * Sidebar navigation component.
 */

import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  FolderKanban,
  FileText,
  ClipboardCheck,
  Settings,
  FlaskConical,
} from "lucide-react";

const navItems = [
  { path: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { path: "/projects", label: "Projects", icon: FolderKanban },
  { path: "/documents", label: "Documents", icon: FileText },
  { path: "/testcases", label: "Test Cases", icon: ClipboardCheck },
];

export function Sidebar() {
  return (
    <aside className="fixed left-0 top-0 h-screen w-64 bg-gray-900 text-white flex flex-col z-40">
      {/* Logo */}
      <div className="px-6 py-5 border-b border-gray-800">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-indigo-600 rounded-lg flex items-center justify-center">
            <FlaskConical className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-sm font-bold tracking-wide">AI Test Engineer</h1>
            <p className="text-xs text-gray-400">v1.0.0</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                isActive
                  ? "bg-indigo-600 text-white"
                  : "text-gray-400 hover:text-white hover:bg-gray-800"
              }`
            }
          >
            <item.icon className="w-5 h-5" />
            {item.label}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="px-4 py-3 border-t border-gray-800">
        <NavLink
          to="/settings"
          className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-gray-400 hover:text-white hover:bg-gray-800 transition-all"
        >
          <Settings className="w-5 h-5" />
          Settings
        </NavLink>
      </div>
    </aside>
  );
}
