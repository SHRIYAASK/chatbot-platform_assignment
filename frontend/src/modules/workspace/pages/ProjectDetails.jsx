import { useParams } from "react-router-dom";
import Loader from "../../../shared/components/Loader.jsx";
import { formatDate } from "../../../shared/utils/formatDate.js";
import { useProject } from "../hooks/useProject.js";

function DetailRow({ label, value }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4">
      <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
        {label}
      </p>
      <p className="mt-2 text-sm text-slate-900">{value}</p>
    </div>
  );
}

export default function ProjectDetails() {
  const { id } = useParams();
  const { project, loading } = useProject(id);

  if (loading) {
    return <Loader label="Loading project..." />;
  }

  if (!project) {
    return null;
  }

  return (
    <main className="mx-auto max-w-4xl px-4 py-8">
      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <h1 className="text-3xl font-bold text-slate-900">{project.title}</h1>
            <p className="mt-2 text-slate-600">{project.description}</p>
          </div>
        </div>

        <div className="mt-6 grid gap-4 sm:grid-cols-2">
          <DetailRow label="Primary AI Model" value={project.primary_model} />
          <DetailRow label="Fallback AI Model" value={project.fallback_model} />
          <DetailRow label="Created Date" value={formatDate(project.created_at)} />
          <DetailRow label="Last Updated" value={formatDate(project.updated_at)} />
        </div>

        <div className="mt-6 rounded-lg border border-dashed border-slate-300 bg-slate-50 p-6 text-center">
          <p className="text-sm text-slate-600">
            Chat module will be implemented next.
          </p>
        </div>
      </div>
    </main>
  );
}
