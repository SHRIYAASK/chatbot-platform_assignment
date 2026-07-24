import { useProjectDocuments } from "../hooks/useProjectDocuments.js";
import { ACCEPTED_DOCUMENT_TYPES, formatFileSize } from "../services/documentService.js";

function StatusBadge({ status }) {
  const styles = {
    ready: "bg-emerald-50 text-emerald-700",
    processing: "bg-amber-50 text-amber-700",
    failed: "bg-rose-50 text-rose-700",
  };

  return (
    <span
      className={`rounded-full px-2 py-0.5 text-[10px] font-medium uppercase tracking-wide ${
        styles[status] || "bg-slate-100 text-slate-600"
      }`}
    >
      {status}
    </span>
  );
}

export default function DocumentUploadPanel({ projectId }) {
  const {
    documents,
    loading,
    uploading,
    deletingId,
    hasProcessingDocuments,
    fileInputRef,
    handleUploadClick,
    handleFileChange,
    handleDelete,
  } = useProjectDocuments(projectId);

  return (
    <div className="mt-4 rounded-lg border border-slate-200 bg-slate-50 p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="text-sm font-semibold text-slate-900">Project documents</h3>
          <p className="mt-1 text-xs text-slate-500">
            Upload files to power retrieval-augmented answers.
          </p>
        </div>
        <button
          type="button"
          onClick={handleUploadClick}
          disabled={uploading}
          className="rounded-md bg-brand-600 px-3 py-1.5 text-xs font-medium text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {uploading ? "Uploading..." : "Upload"}
        </button>
      </div>

      {hasProcessingDocuments ? (
        <p className="mt-3 text-xs text-amber-700">
          Indexing uploaded documents. This may take a moment for large PDFs.
        </p>
      ) : null}

      <input
        ref={fileInputRef}
        type="file"
        accept={ACCEPTED_DOCUMENT_TYPES}
        className="hidden"
        onChange={handleFileChange}
      />

      <div className="mt-4 space-y-2">
        {loading ? (
          <p className="text-xs text-slate-500">Loading documents...</p>
        ) : documents.length === 0 ? (
          <p className="rounded-md border border-dashed border-slate-300 bg-white px-3 py-4 text-xs text-slate-500">
            No documents yet. Upload PDF, TXT, MD, JSON, or DOCX files up to 10 MB.
          </p>
        ) : (
          documents.map((document) => (
            <div
              key={document.id}
              className="flex items-start justify-between gap-3 rounded-md border border-slate-200 bg-white px-3 py-2"
            >
              <div className="min-w-0">
                <p className="truncate text-xs font-medium text-slate-900">{document.filename}</p>
                <div className="mt-1 flex items-center gap-2">
                  <span className="text-[11px] text-slate-500">
                    {formatFileSize(document.file_size)}
                  </span>
                  <StatusBadge status={document.status} />
                </div>
                {document.status === "failed" && document.failure_reason ? (
                  <p className="mt-1 text-[11px] leading-snug text-rose-600">
                    {document.failure_reason}
                  </p>
                ) : null}
              </div>
              <button
                type="button"
                onClick={() => handleDelete(document.id)}
                disabled={deletingId === document.id || document.status === "processing"}
                className="shrink-0 text-[11px] font-medium text-rose-600 hover:text-rose-700 disabled:opacity-50"
              >
                {deletingId === document.id ? "Removing..." : "Remove"}
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
