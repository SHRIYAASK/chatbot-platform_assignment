import { createContext, useCallback, useContext, useMemo, useState } from "react";

const ToastContext = createContext(null);

export function ToastProvider({ children }) {
  const [toast, setToast] = useState(null);

  const showToast = useCallback((message, type = "info") => {
    setToast({ message, type });
    window.setTimeout(() => setToast(null), 3500);
  }, []);

  const showSuccess = useCallback(
    (message) => showToast(message, "success"),
    [showToast]
  );
  const showError = useCallback(
    (message) => showToast(message, "error"),
    [showToast]
  );
  const showInfo = useCallback(
    (message) => showToast(message, "info"),
    [showToast]
  );

  const value = useMemo(
    () => ({
      toast,
      showToast,
      showSuccess,
      showError,
      showInfo,
    }),
    [toast, showToast, showSuccess, showError, showInfo]
  );

  return <ToastContext.Provider value={value}>{children}</ToastContext.Provider>;
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error("useToast must be used within a ToastProvider");
  }
  return context;
}
