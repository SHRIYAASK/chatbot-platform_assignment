import { formatApiDetail } from "./formatApiDetail.js";

export function mapApiError(status, detail, fallbackMessage) {
  if (status === 409) {
    return formatApiDetail(detail, "Project already exists.");
  }
  if (status === 403) {
    return formatApiDetail(detail, "You do not have permission to access this project.");
  }
  if (status === 404) {
    return formatApiDetail(detail, "Project not found.");
  }
  if (status === 422) {
    return formatApiDetail(detail, fallbackMessage);
  }
  if (status === 429) {
    return formatApiDetail(detail, "Too many requests. Please wait a moment and try again.");
  }
  if (status === 500) {
    return formatApiDetail(detail, fallbackMessage);
  }
  return formatApiDetail(detail, fallbackMessage);
}

export function mapNetworkError(error, fallbackMessage = "An unexpected error occurred.") {
  if (!error.response) {
    const apiUrl = import.meta.env.VITE_API_URL || "http://127.0.0.1:8002";
    return `Cannot reach the backend at ${apiUrl}. Check that the API is running and VITE_API_URL is set on Vercel.`;
  }

  const status = error.response.status;
  const detail = error.response.data?.detail;

  if (status === 503) {
    return formatApiDetail(detail, "Database connection failure.");
  }
  if (status === 500) {
    return formatApiDetail(detail, fallbackMessage);
  }
  if (status === 429) {
    return formatApiDetail(detail, "Too many requests. Please wait a moment and try again.");
  }
  if (status === 401) {
    return "Session expired. Please log in again.";
  }
  if (status === 403) {
    return formatApiDetail(detail, "You are not authorized to perform this action.");
  }
  if (status === 422) {
    return formatApiDetail(detail, fallbackMessage);
  }

  return formatApiDetail(detail, fallbackMessage);
}
