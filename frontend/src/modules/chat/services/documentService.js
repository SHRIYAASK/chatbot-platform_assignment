import api from "../../../shared/api/axios.js";

export async function listDocuments(projectId, { signal } = {}) {
  const response = await api.get(`/projects/${projectId}/documents`, { signal });
  return response.data;
}

export async function uploadDocument(projectId, file, { signal, onUploadProgress } = {}) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await api.post(`/projects/${projectId}/documents`, formData, {
    signal,
    onUploadProgress,
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
}

export async function deleteDocument(projectId, documentId, { signal } = {}) {
  await api.delete(`/projects/${projectId}/documents/${documentId}`, { signal });
}

export function formatFileSize(bytes) {
  if (bytes < 1024) {
    return `${bytes} B`;
  }
  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export const ACCEPTED_DOCUMENT_TYPES = ".txt,.pdf,.md,.json,.docx";
