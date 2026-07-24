export function mapApiError(status, detail, fallbackMessage) {
  if (status === 409) {
    return detail || "Project already exists.";
  }
  if (status === 403) {
    return detail || "You do not have permission to access this project.";
  }
  if (status === 404) {
    return detail || "Project not found.";
  }
  if (status === 500) {
    return detail || fallbackMessage;
  }
  return detail || fallbackMessage;
}

export function mapNetworkError(error, fallbackMessage = "An unexpected error occurred.") {
  if (!error.response) {
    const apiUrl = import.meta.env.VITE_API_URL || "http://127.0.0.1:8002";
    return `Cannot reach the backend. Make sure it is running at ${apiUrl}.`;
  }

  const status = error.response.status;
  const detail = error.response.data?.detail;

  if (status === 503) {
    return detail || "Database connection failure.";
  }
  if (status === 500) {
    return detail || fallbackMessage;
  }
  if (status === 401) {
    return "Session expired. Please log in again.";
  }

  return detail || fallbackMessage;
}
