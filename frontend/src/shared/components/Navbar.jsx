import { Link, useLocation } from "react-router-dom";
import { ArrowLeft, LogOut } from "lucide-react";
import { PRODUCT_NAME } from "../config/branding.js";

export default function Navbar({ user, onLogout }) {
  const location = useLocation();
  const showBackButton = location.pathname.startsWith("/projects/");

  return (
    <header className="sticky top-0 z-40 border-b border-slate-200/80 bg-white/85 backdrop-blur-md">
      <div className="flex w-full items-center justify-between px-4 py-3.5 sm:px-6">
        <div className="flex items-center gap-3">
          {showBackButton ? (
            <Link
              to="/dashboard"
              aria-label="Back to dashboard"
              className="rounded-xl p-1.5 text-brand-600 transition hover:bg-brand-50 hover:text-brand-700"
            >
              <ArrowLeft className="h-5 w-5" />
            </Link>
          ) : null}
          <Link to="/dashboard" className="flex items-center gap-2 text-lg font-semibold text-brand-700">
            <span className="flex h-8 w-8 items-center justify-center rounded-xl bg-brand-600 text-sm font-bold text-white shadow-sm">
              S
            </span>
            {PRODUCT_NAME}
          </Link>
        </div>
        <div className="flex items-center gap-3">
          {user ? (
            <span className="hidden rounded-full bg-slate-100 px-3 py-1 text-sm text-slate-600 sm:inline">
              {user.name}
            </span>
          ) : null}
          {onLogout ? (
            <button
              type="button"
              onClick={onLogout}
              aria-label="Logout"
              className="rounded-xl p-1.5 text-slate-500 transition hover:bg-slate-100 hover:text-slate-700 focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2"
            >
              <LogOut className="h-5 w-5" />
            </button>
          ) : null}
        </div>
      </div>
    </header>
  );
}
