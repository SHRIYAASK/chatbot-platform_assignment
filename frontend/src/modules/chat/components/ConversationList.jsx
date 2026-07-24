import { useState } from "react";
import { Search } from "lucide-react";
import ConversationItem from "./ConversationItem.jsx";
import DeleteConversationDialog from "./DeleteConversationDialog.jsx";
import RenameConversationDialog from "./RenameConversationDialog.jsx";

export function ConversationSearchInput({ value, onChange }) {
  return (
    <div className="relative">
      <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
      <input
        type="search"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder="Search chats"
        className="w-full rounded-lg border border-slate-300 bg-white py-2 pl-9 pr-3 text-sm text-slate-900 shadow-sm placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500"
      />
    </div>
  );
}

export default function ConversationList({
  conversations,
  loading,
  activeConversationId,
  renamingId,
  deletingId,
  onSelect,
  onRename,
  onDelete,
}) {
  const [renameTarget, setRenameTarget] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);

  if (loading) {
    return <p className="px-1 py-2 text-xs text-slate-500">Loading conversations...</p>;
  }

  if (conversations.length === 0) {
    return (
      <p className="rounded-lg border border-dashed border-slate-300 bg-slate-50 px-3 py-4 text-xs text-slate-500">
        No conversations yet. Start a new chat to begin.
      </p>
    );
  }

  return (
    <>
      <ul className="space-y-1">
        {conversations.map((conversation) => (
          <li key={conversation.id}>
            <ConversationItem
              conversation={conversation}
              isActive={String(conversation.id) === String(activeConversationId)}
              isRenaming={renamingId === conversation.id}
              isDeleting={deletingId === conversation.id}
              onSelect={onSelect}
              onRename={() => setRenameTarget(conversation)}
              onDelete={() => setDeleteTarget(conversation)}
            />
          </li>
        ))}
      </ul>

      <RenameConversationDialog
        isOpen={Boolean(renameTarget)}
        conversation={renameTarget}
        submitting={Boolean(renameTarget && renamingId === renameTarget.id)}
        onClose={() => setRenameTarget(null)}
        onConfirm={onRename}
      />

      <DeleteConversationDialog
        isOpen={Boolean(deleteTarget)}
        conversation={deleteTarget}
        submitting={Boolean(deleteTarget && deletingId === deleteTarget.id)}
        onClose={() => setDeleteTarget(null)}
        onConfirm={onDelete}
      />
    </>
  );
}
