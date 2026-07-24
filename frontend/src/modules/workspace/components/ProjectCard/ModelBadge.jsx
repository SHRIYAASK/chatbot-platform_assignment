export default function ModelBadge({ model }) {
  if (!model) {
    return null;
  }

  return (
    <div className="flex items-center justify-between gap-4">
      <span className="shrink-0 text-[11px] font-medium uppercase tracking-wide text-slate-500">
        Current Model
      </span>
      <span className="truncate text-right text-sm font-medium text-slate-900">{model}</span>
    </div>
  );
}
