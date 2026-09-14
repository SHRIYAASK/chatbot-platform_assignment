export default function Input({
  label,
  id,
  error,
  className = "",
  ...props
}) {
  return (
    <div className="space-y-1">
      {label ? (
        <label htmlFor={id} className="block text-sm font-medium text-slate-700">
          {label}
        </label>
      ) : null}
      <input
        id={id}
        className={`w-full rounded-xl border bg-white px-3 py-2.5 text-sm shadow-sm transition placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500 ${
          error ? "border-red-500" : "border-slate-200 focus:border-brand-400"
        } ${className}`}
        {...props}
      />
      {error ? <p className="text-sm text-red-600">{error}</p> : null}
    </div>
  );
}
