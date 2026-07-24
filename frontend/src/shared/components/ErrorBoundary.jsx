import { Component } from "react";
import Button from "./Button.jsx";

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex min-h-[320px] items-center justify-center px-4">
          <div className="max-w-md rounded-2xl border border-slate-200 bg-white p-6 text-center shadow-sm">
            <h1 className="text-lg font-semibold text-slate-900">Something went wrong</h1>
            <p className="mt-2 text-sm text-slate-600">
              An unexpected error occurred. Reload the page or return to the dashboard.
            </p>
            <div className="mt-4 flex justify-center gap-3">
              <Button type="button" onClick={() => window.location.reload()}>
                Reload
              </Button>
              <Button
                type="button"
                variant="secondary"
                onClick={() => {
                  window.location.href = "/dashboard";
                }}
              >
                Dashboard
              </Button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
