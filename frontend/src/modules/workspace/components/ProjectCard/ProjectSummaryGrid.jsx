function formatStorageMb(value = 0) {
  if (value >= 10) {
    return `${Math.round(value)} MB`;
  }

  if (Number.isInteger(value)) {
    return `${value} MB`;
  }

  return `${value.toFixed(1)} MB`;
}

function formatCount(value = 0) {
  return new Intl.NumberFormat("en-US").format(value);
}

function SummaryCell({ label, value }) {
  return (
    <div className="flex min-h-[4.5rem] flex-col justify-center px-3 py-2.5">
      <p className="text-[11px] font-medium uppercase tracking-wide text-slate-500">
        {label}
      </p>
      <p className="mt-1 text-lg font-semibold tabular-nums text-slate-900">{value}</p>
    </div>
  );
}

export default function ProjectSummaryGrid({ summary }) {
  const data = summary ?? {
    messages: 0,
    conversations: 0,
    documents: 0,
    storage_mb: 0,
  };

  return (
    <div className="overflow-hidden rounded-lg border border-slate-200 bg-slate-50">
      <div className="grid grid-cols-2 divide-x divide-slate-200 border-b border-slate-200">
        <SummaryCell label="Messages" value={formatCount(data.messages)} />
        <SummaryCell label="Chats" value={formatCount(data.conversations)} />
      </div>
      <div className="grid grid-cols-2 divide-x divide-slate-200">
        <SummaryCell label="Documents" value={formatCount(data.documents)} />
        <SummaryCell label="Storage" value={formatStorageMb(data.storage_mb)} />
      </div>
    </div>
  );
}
