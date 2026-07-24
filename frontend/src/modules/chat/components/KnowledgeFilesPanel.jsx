import { FileText, Upload } from "lucide-react";
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

export default function KnowledgeFilesPanel({ projectId, documentState }) {
  const hookState = useProjectDocuments(documentState ? null : projectId);
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
  } = documentState || hookState;

  return (
    <section className="border-t border-slate-200 pt-4">
      <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
        Knowledge Files
      </h3>

      {hasProcessingDocuments ? (
        <p className="mt-2 text-xs text-amber-700">
          Indexing uploaded documents. Large files may take a moment.
        </p>
      ) : null}

      <input
        ref={fileInputRef}
        type="file"
        accept={ACCEPTED_DOCUMENT_TYPES}
        className="hidden"
        onChange={handleFileChange}
      />

      <div className="mt-3 space-y-2">
        {loading ? (
          <p className="text-xs text-slate-500">Loading files...</p>
        ) : documents.length === 0 ? (
          <p className="rounded-lg border border-dashed border-slate-300 bg-slate-50 px-3 py-3 text-xs text-slate-500">
            No files uploaded yet.
          </p>
        ) : (
          documents.map((document) => (
            <div
              key={document.id}
              className="flex items-start justify-between gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2"
            >
              <div className="min-w-0">
                <div className="flex items-center gap-2">
                  <FileText className="h-3.5 w-3.5 shrink-0 text-slate-400" />
                  <p className="truncate text-xs font-medium text-slate-900">
                    {document.filename}
                  </p>
                </div>
                <div className="mt-1 flex items-center gap-2 pl-5">
                  <span className="text-[11px] text-slate-500">
                    {formatFileSize(document.file_size)}
                  </span>
                  <StatusBadge status={document.status} />
                </div>
                {document.status === "failed" && document.failure_reason ? (
                  <p className="mt-1 pl-5 text-[11px] leading-snug text-rose-600">
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
                {deletingId === document.id ? "..." : "Delete"}
              </button>
            </div>
          ))
        )}
      </div>

      <button
        type="button"
        onClick={handleUploadClick}
        disabled={uploading}
        className="mt-3 flex w-full items-center justify-center gap-2 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
      >
        <Upload className="h-4 w-4" />
        {uploading ? "Uploading..." : "Upload File"}
      </button>
    </section>
  );
}
