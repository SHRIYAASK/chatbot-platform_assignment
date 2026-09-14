export default function ChatHeader({ project }) {
  return (
    <header className="border-b border-slate-200/80 bg-white/90 px-4 py-4 backdrop-blur-sm sm:px-6">
      <div>
        <h1 className="text-xl font-bold tracking-tight text-slate-900 sm:text-2xl">{project?.title}</h1>
        <p className="mt-1 line-clamp-2 text-sm text-slate-600">{project?.description}</p>
      </div>
    </header>
  );
}
