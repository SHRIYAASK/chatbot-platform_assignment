import { useEffect, useRef, useState } from "react";
import { Navigate, useNavigate, useParams } from "react-router-dom";
import Loader from "../../../shared/components/Loader.jsx";
import { useProject } from "../../workspace/hooks/useProject.js";
import ChatHeader from "../components/ChatHeader.jsx";
import ChatSidebar from "../components/ChatSidebar.jsx";
import ChatWindow from "../components/ChatWindow.jsx";
import { useChat } from "../hooks/useChat.js";
import { useConversations } from "../hooks/useConversations.js";
import { useInfiniteChat } from "../hooks/useInfiniteChat.js";
import { useProjectDocuments } from "../hooks/useProjectDocuments.js";

export default function ProjectChat() {
  const { id: projectId, conversationId: conversationIdParam } = useParams();
  const navigate = useNavigate();
  const activeConversationId = conversationIdParam ? Number(conversationIdParam) : null;
  const [focusInputToken, setFocusInputToken] = useState(0);
  const [bootstrapping, setBootstrapping] = useState(!activeConversationId);
  const redirectAttemptedRef = useRef(false);

  const { project, loading: projectLoading } = useProject(projectId);
  const documentState = useProjectDocuments(projectId);
  const {
    conversations,
    loading: conversationsLoading,
    creating,
    renamingId,
    deletingId,
    selectConversation,
    createNewConversation,
    renameConversation,
    deleteConversation,
    refreshConversations,
  } = useConversations(projectId, activeConversationId);

  const resolvedConversationId = conversations.some(
    (conversation) => conversation.id === activeConversationId,
  )
    ? activeConversationId
    : null;

  const {
    messages,
    loading: messagesLoading,
    loadingOlder,
    hasMore,
    handleScroll,
    appendOptimisticUserMessage,
    finalizeMessages,
    syncMessages,
  } = useInfiniteChat(projectId, resolvedConversationId);

  const { isGenerating, typing, sendChatMessage, stopGeneration } = useChat(
    projectId,
    resolvedConversationId,
    {
      appendOptimisticUserMessage,
      finalizeMessages,
      syncMessages,
      onMessageSent: refreshConversations,
    },
  );

  useEffect(() => {
    redirectAttemptedRef.current = false;
    setBootstrapping(!conversationIdParam);
  }, [projectId, conversationIdParam]);

  useEffect(() => {
    if (projectLoading || conversationsLoading || !bootstrapping) {
      return;
    }
    if (redirectAttemptedRef.current) {
      return;
    }

    redirectAttemptedRef.current = true;

    const openConversation = async () => {
      if (conversations.length > 0) {
        navigate(`/projects/${projectId}/c/${conversations[0].id}`, { replace: true });
        return;
      }

      const conversation = await createNewConversation();
      if (!conversation) {
        redirectAttemptedRef.current = false;
        setBootstrapping(false);
      }
    };

    openConversation();
  }, [
    projectLoading,
    conversationsLoading,
    bootstrapping,
    conversations,
    projectId,
    navigate,
    createNewConversation,
  ]);

  useEffect(() => {
    if (!bootstrapping && activeConversationId && conversationsLoading) {
      return;
    }

    if (!activeConversationId || conversationsLoading) {
      return;
    }

    const belongsToProject = conversations.some(
      (conversation) => conversation.id === activeConversationId,
    );

    if (!belongsToProject) {
      if (conversations.length > 0) {
        navigate(`/projects/${projectId}/c/${conversations[0].id}`, { replace: true });
        return;
      }

      if (!creating) {
        createNewConversation();
      }
    }
  }, [
    activeConversationId,
    conversations,
    conversationsLoading,
    bootstrapping,
    creating,
    projectId,
    navigate,
    createNewConversation,
  ]);

  useEffect(() => {
    if (activeConversationId && resolvedConversationId) {
      setFocusInputToken((current) => current + 1);
      setBootstrapping(false);
    }
  }, [activeConversationId, resolvedConversationId]);

  const handleCreateConversation = async () => {
    const conversation = await createNewConversation();
    if (conversation) {
      setFocusInputToken((current) => current + 1);
      setBootstrapping(false);
    }
  };

  if (projectLoading || (conversationsLoading && bootstrapping)) {
    return <Loader label="Loading project..." />;
  }

  if (!project) {
    return <Navigate to="/dashboard" replace />;
  }

  if (bootstrapping || !resolvedConversationId) {
    return <Loader label="Opening conversation..." />;
  }

  return (
    <div className="flex h-[calc(100vh-73px)] flex-col">
      <ChatHeader project={project} />
      <div className="flex min-h-0 flex-1">
        <ChatSidebar
          project={project}
          documentState={documentState}
          conversations={conversations}
          conversationsLoading={conversationsLoading}
          creatingConversation={creating}
          renamingId={renamingId}
          deletingId={deletingId}
          activeConversationId={resolvedConversationId}
          onSelectConversation={selectConversation}
          onCreateConversation={handleCreateConversation}
          onRenameConversation={renameConversation}
          onDeleteConversation={deleteConversation}
        />
        <div className="flex min-w-0 flex-1 flex-col">
          <ChatWindow
            messages={messages}
            loading={messagesLoading}
            loadingOlder={loadingOlder}
            hasMore={hasMore}
            onScroll={handleScroll}
            typing={typing}
            isGenerating={isGenerating}
            onSend={sendChatMessage}
            onStop={stopGeneration}
            focusInputToken={focusInputToken}
          />
        </div>
      </div>
    </div>
  );
}
