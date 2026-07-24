import { useNavigate } from "react-router-dom";
import Button from "../../../../shared/components/Button.jsx";
import { formatDate } from "../../../../shared/utils/formatDate.js";
import ModelBadge from "./ModelBadge.jsx";
import ProjectSummaryGrid from "./ProjectSummaryGrid.jsx";

function EditIcon() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="h-4 w-4"
      aria-hidden="true"
    >
      <path d="M12 20h9" />
      <path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z" />
    </svg>
  );
}

function DeleteIcon() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="h-4 w-4"
      aria-hidden="true"
    >
      <path d="M3 6h18" />
      <path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
      <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6" />
      <path d="M10 11v6" />
      <path d="M14 11v6" />
    </svg>
  );
}

export default function ProjectCard({ project, onEdit, onDelete }) {
  const navigate = useNavigate();

  return (
    <article className="flex h-full flex-col rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition hover:shadow-md">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold text-slate-900">{project.title}</h3>
          <p className="mt-1 text-xs text-slate-500">
            Created {formatDate(project.created_at)}
          </p>
        </div>
        <div className="flex shrink-0 items-center gap-1">
          <button
            type="button"
            onClick={() => onEdit(project)}
            aria-label={`Edit ${project.title}`}
            className="rounded-lg p-2 text-slate-500 transition hover:bg-slate-100 hover:text-brand-600 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:ring-offset-2"
          >
            <EditIcon />
          </button>
          <button
            type="button"
            onClick={() => onDelete(project)}
            aria-label={`Delete ${project.title}`}
            className="rounded-lg p-2 text-slate-500 transition hover:bg-red-50 hover:text-red-600 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
          >
            <DeleteIcon />
          </button>
        </div>
      </div>

      <p className="mt-3 flex-1 text-justify text-sm leading-relaxed text-slate-600">
        {project.description}
      </p>

      <div className="mt-4 space-y-3 border-t border-slate-200 pt-4">
        <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
          Project Summary
        </p>
        <ProjectSummaryGrid summary={project.summary} />
        <ModelBadge model={project.summary?.model} />
      </div>

      <div className="mt-4 border-t border-slate-200 pt-4">
        <Button
          className="w-full"
          variant="secondary"
          onClick={() => navigate(`/projects/${project.id}`)}
        >
          Open
        </Button>
      </div>
    </article>
  );
}
