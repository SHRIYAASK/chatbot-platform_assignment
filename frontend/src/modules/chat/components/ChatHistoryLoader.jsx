function HistorySpinner() {
  return (
    <div className="flex justify-center py-3" aria-live="polite" aria-busy="true">
      <div className="h-6 w-6 animate-spin rounded-full border-2 border-slate-200 border-t-brand-600" />
      <span className="sr-only">Loading older messages</span>
    </div>
  );
}

export default function ChatHistoryLoader({ loadingOlder, hasMore }) {
  if (!loadingOlder && !hasMore) {
    return null;
  }

  return (
    <div className="mx-auto w-full max-w-4xl">
      {loadingOlder ? <HistorySpinner /> : null}
    </div>
  );
}
