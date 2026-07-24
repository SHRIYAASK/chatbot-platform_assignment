import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useToast } from "../../../shared/hooks/useToast.jsx";
import {
  createConversation,
  deleteConversation as deleteConversationRequest,
  fetchConversations,
  updateConversation as updateConversationRequest,
} from "../services/conversationService.js";

export function useConversations(projectId, activeConversationId) {
  const navigate = useNavigate();
  const { showError, showSuccess } = useToast();
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [renamingId, setRenamingId] = useState(null);
  const [deletingId, setDeletingId] = useState(null);

  useEffect(() => {
    setConversations([]);
    setLoading(Boolean(projectId));
  }, [projectId]);

  const loadConversations = useCallback(
    async ({ silent = false } = {}) => {
      if (!projectId) {
        return [];
      }

      if (!silent) {
        setLoading(true);
      }

      try {
        const data = await fetchConversations(projectId);
        const nextConversations = data.conversations || [];
        setConversations(nextConversations);
        return nextConversations;
      } catch (error) {
        if (!silent) {
          showError(error.response?.data?.detail || "Failed to load conversations.");
          setConversations([]);
        }
        return [];
      } finally {
        if (!silent) {
          setLoading(false);
        }
      }
    },
    [projectId, showError],
  );

  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  const selectConversation = useCallback(
    (conversationId) => {
      if (!projectId || !conversationId) {
        return;
      }
      navigate(`/projects/${projectId}/c/${conversationId}`);
    },
    [navigate, projectId],
  );

  const createNewConversation = useCallback(async () => {
    if (!projectId || creating) {
      return null;
    }

    setCreating(true);
    try {
      const conversation = await createConversation(projectId);
      setConversations((current) => [conversation, ...current]);
      navigate(`/projects/${projectId}/c/${conversation.id}`);
      return conversation;
    } catch (error) {
      showError(error.response?.data?.detail || "Failed to create conversation.");
      return null;
    } finally {
      setCreating(false);
    }
  }, [projectId, creating, navigate, showError]);

  const renameConversation = useCallback(
    async (conversationId, title) => {
      if (!projectId) {
        return false;
      }

      setRenamingId(conversationId);
      try {
        const updated = await updateConversationRequest(projectId, conversationId, { title });
        setConversations((current) =>
          current.map((conversation) =>
            conversation.id === conversationId ? updated : conversation,
          ),
        );
        showSuccess("Conversation renamed successfully.");
        return true;
      } catch (error) {
        const detail = error.response?.data?.detail;
        const message = Array.isArray(detail)
          ? detail.map((item) => item.msg).join(" ")
          : detail || "Unable to rename conversation.";
        showError(message);
        return false;
      } finally {
        setRenamingId(null);
      }
    },
    [projectId, showError, showSuccess],
  );

  const deleteConversation = useCallback(
    async (conversationId) => {
      if (!projectId) {
        return false;
      }

      setDeletingId(conversationId);
      const wasActive = Number(activeConversationId) === Number(conversationId);

      try {
        await deleteConversationRequest(projectId, conversationId);
        const remaining = conversations.filter(
          (conversation) => conversation.id !== conversationId,
        );
        setConversations(remaining);
        showSuccess("Conversation deleted successfully.");

        if (wasActive) {
          if (remaining.length > 0) {
            navigate(`/projects/${projectId}/c/${remaining[0].id}`, { replace: true });
          } else {
            setCreating(true);
            try {
              const conversation = await createConversation(projectId);
              setConversations([conversation]);
              navigate(`/projects/${projectId}/c/${conversation.id}`, { replace: true });
            } catch (error) {
              showError(error.response?.data?.detail || "Unable to delete conversation.");
              return false;
            } finally {
              setCreating(false);
            }
          }
        }

        return true;
      } catch (error) {
        showError(error.response?.data?.detail || "Unable to delete conversation.");
        return false;
      } finally {
        setDeletingId(null);
      }
    },
    [
      projectId,
      activeConversationId,
      conversations,
      navigate,
      showError,
      showSuccess,
    ],
  );

  const refreshConversations = useCallback(async () => {
    return loadConversations({ silent: true });
  }, [loadConversations]);

  return {
    conversations,
    loading,
    creating,
    renamingId,
    deletingId,
    activeConversationId,
    selectConversation,
    createNewConversation,
    renameConversation,
    deleteConversation,
    refreshConversations,
    reloadConversations: loadConversations,
  };
}
