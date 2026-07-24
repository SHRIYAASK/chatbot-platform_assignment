import { Link, useLocation } from "react-router-dom";
import { ArrowLeft, LogOut } from "lucide-react";

export default function Navbar({ user, onLogout }) {
  const location = useLocation();
  const showBackButton = location.pathname.startsWith("/projects/");

  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="flex w-full items-center justify-between px-4 py-4 sm:px-6">
        <div className="flex items-center gap-3">
          {showBackButton ? (
            <Link
              to="/dashboard"
              aria-label="Back to dashboard"
              className="rounded-lg p-1.5 text-brand-600 transition hover:bg-brand-50 hover:text-brand-700"
            >
              <ArrowLeft className="h-5 w-5" />
            </Link>
          ) : null}
          <Link to="/dashboard" className="text-lg font-semibold text-brand-700">
            Chatbot Platform
          </Link>
        </div>
        <div className="flex items-center gap-4">
          {user ? (
            <span className="text-sm text-slate-600">Welcome, {user.name}</span>
          ) : null}
          {onLogout ? (
            <button
              type="button"
              onClick={onLogout}
              aria-label="Logout"
              className="rounded-lg p-1.5 text-slate-500 transition hover:bg-slate-100 hover:text-slate-700 focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2"
            >
              <LogOut className="h-5 w-5" />
            </button>
          ) : null}
        </div>
      </div>
    </header>
  );
}
