import axios from "axios";
import { clearToken, getToken } from "../utils/token.js";

const configuredApiUrl = import.meta.env.VITE_API_URL?.trim();

if (import.meta.env.PROD && !configuredApiUrl) {
  console.error(
    "VITE_API_URL is not set. Add it in Vercel → Project Settings → Environment Variables, then redeploy.",
  );
}

const api = axios.create({
  baseURL: configuredApiUrl || "http://127.0.0.1:8002",
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

function shouldRedirectToLogin() {
  const path = window.location.pathname || "";
  return !path.startsWith("/login") && !path.startsWith("/register");
}

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      clearToken();
      if (shouldRedirectToLogin()) {
        const next = `${window.location.pathname}${window.location.search}`;
        const params = new URLSearchParams({ reason: "session_expired", next });
        window.location.assign(`/login?${params.toString()}`);
      }
    }
    return Promise.reject(error);
  },
);

export default api;
