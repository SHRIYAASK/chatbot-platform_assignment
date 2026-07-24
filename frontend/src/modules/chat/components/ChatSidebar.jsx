import { Link } from "react-router-dom";
import { Plus, Settings } from "lucide-react";
import ConversationList from "./ConversationList.jsx";
import KnowledgeFilesPanel from "./KnowledgeFilesPanel.jsx";

export default function ChatSidebar({
  project,
  documentState,
  conversations,
  conversationsLoading,
  creatingConversation,
  renamingId,
  deletingId,
  activeConversationId,
  onSelectConversation,
  onCreateConversation,
  onRenameConversation,
  onDeleteConversation,
}) {
  return (
    <aside className="hidden w-80 shrink-0 flex-col border-r border-slate-200 bg-white lg:flex">
      <div className="flex min-h-0 flex-1 flex-col overflow-hidden">
        <div className="border-b border-slate-200 px-4 py-4">
          <button
            type="button"
            onClick={onCreateConversation}
            disabled={creatingConversation}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-brand-600 px-3 py-2.5 text-sm font-medium text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            <Plus className="h-4 w-4" />
            {creatingConversation ? "Creating..." : "New Chat"}
          </button>
        </div>

        <div className="min-h-0 flex-1 overflow-y-auto px-4 py-4 pr-3">
          <ConversationList
            conversations={conversations}
            loading={conversationsLoading}
            activeConversationId={activeConversationId}
            renamingId={renamingId}
            deletingId={deletingId}
            onSelect={onSelectConversation}
            onRename={onRenameConversation}
            onDelete={onDeleteConversation}
          />
        </div>

        <div className="shrink-0 space-y-4 overflow-y-auto px-4 pb-4">
          <KnowledgeFilesPanel projectId={project.id} documentState={documentState} />

          <Link
            to={`/projects/${project.id}/settings`}
            className="flex items-center gap-2 rounded-lg border border-slate-200 px-3 py-2.5 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
          >
            <Settings className="h-4 w-4 text-slate-500" />
            Project Settings
          </Link>
        </div>
      </div>
    </aside>
  );
}
