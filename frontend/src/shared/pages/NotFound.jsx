import { Link } from "react-router-dom";
import Button from "../components/Button.jsx";

export default function NotFound() {
  return (
    <div className="flex min-h-[calc(100vh-73px)] items-center justify-center px-4">
      <div className="max-w-md text-center">
        <h1 className="text-3xl font-bold text-slate-900">404</h1>
        <p className="mt-2 text-slate-600">The page you requested could not be found.</p>
        <Link to="/dashboard" className="mt-6 inline-block">
          <Button type="button">Back to Dashboard</Button>
        </Link>
      </div>
    </div>
  );
}
