import { Link } from "react-router-dom";
import Button from "../components/Button.jsx";

export default function NotFound() {
  return (
    <div className="flex min-h-[calc(100vh-4.25rem)] items-center justify-center px-4">
      <div className="card-surface max-w-md p-8 text-center">
        <p className="text-sm font-semibold uppercase tracking-wide text-brand-600">404</p>
        <h1 className="mt-2 text-3xl font-bold text-slate-900">Page not found</h1>
        <p className="mt-2 text-slate-600">The page you requested could not be found.</p>
        <Link to="/dashboard" className="mt-6 inline-block">
          <Button type="button">Back to Dashboard</Button>
        </Link>
      </div>
    </div>
  );
}
