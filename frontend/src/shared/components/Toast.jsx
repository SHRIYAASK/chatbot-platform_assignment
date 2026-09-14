import { useToast } from "../hooks/useToast.jsx";

const styles = {
  success: "bg-emerald-600",
  error: "bg-red-600",
  info: "bg-brand-600",
};

export default function Toast() {
  const { toast } = useToast();

  if (!toast) {
    return null;
  }

  return (
    <div className="fixed bottom-6 right-6 z-[60] max-w-sm">
      <div
        className={`rounded-xl px-4 py-3 text-sm font-medium text-white shadow-card ${styles[toast.type] || styles.info}`}
      >
        {toast.message}
      </div>
    </div>
  );
}
