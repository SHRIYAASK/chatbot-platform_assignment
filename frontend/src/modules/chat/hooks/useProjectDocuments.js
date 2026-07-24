import { useCallback, useEffect, useRef, useState } from "react";
import { useToast } from "../../../shared/hooks/useToast.jsx";
import {
  deleteDocument,
  listDocuments,
  uploadDocument,
} from "../services/documentService.js";

const PROCESSING_POLL_MS = 2000;

export function useProjectDocuments(projectId) {
  const { showSuccess, showError } = useToast();
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [deletingId, setDeletingId] = useState(null);
  const fileInputRef = useRef(null);
  const showErrorRef = useRef(showError);

  useEffect(() => {
    showErrorRef.current = showError;
  }, [showError]);

  const loadDocuments = useCallback(async ({ silent = false } = {}) => {
    if (!projectId) {
      return null;
    }

    if (!silent) {
      setLoading(true);
    }
    try {
      const data = await listDocuments(projectId);
      const nextDocuments = data.documents || [];
      setDocuments(nextDocuments);
      return nextDocuments;
    } catch (error) {
      if (!silent) {
        showErrorRef.current(error.response?.data?.detail || "Failed to load documents.");
        setDocuments([]);
      }
      return [];
    } finally {
      if (!silent) {
        setLoading(false);
      }
    }
  }, [projectId]);

  useEffect(() => {
    loadDocuments();
  }, [loadDocuments]);

  const hasProcessingDocuments = documents.some(
    (document) => document.status === "processing",
  );

  useEffect(() => {
    if (!hasProcessingDocuments) {
      return undefined;
    }

    const intervalId = window.setInterval(() => {
      loadDocuments({ silent: true });
    }, PROCESSING_POLL_MS);

    return () => window.clearInterval(intervalId);
  }, [hasProcessingDocuments, loadDocuments]);

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (event) => {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file || !projectId) {
      return;
    }

    setUploading(true);
    try {
      const result = await uploadDocument(projectId, file);
      setDocuments((current) => [result.document, ...current]);
      showSuccess(`"${result.document.filename}" uploaded. Indexing in background...`);
    } catch (error) {
      showError(error.response?.data?.detail || "Failed to upload document.");
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (documentId) => {
    if (!projectId) {
      return;
    }

    setDeletingId(documentId);
    try {
      await deleteDocument(projectId, documentId);
      setDocuments((current) => current.filter((document) => document.id !== documentId));
      showSuccess("Document removed.");
    } catch (error) {
      showError(error.response?.data?.detail || "Failed to delete document.");
    } finally {
      setDeletingId(null);
    }
  };

  return {
    documents,
    loading,
    uploading,
    deletingId,
    hasProcessingDocuments,
    fileInputRef,
    handleUploadClick,
    handleFileChange,
    handleDelete,
    reloadDocuments: loadDocuments,
  };
}
