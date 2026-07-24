export default function ChatHeader({ project }) {
  return (
    <header className="border-b border-slate-200 bg-white px-4 py-4 sm:px-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">{project?.title}</h1>
        <p className="mt-1 text-sm text-slate-600">{project?.description}</p>
      </div>
    </header>
  );
}
