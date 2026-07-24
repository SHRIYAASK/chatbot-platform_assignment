import { MessageSquare } from "lucide-react";
import { formatRelativeTime } from "../../../shared/utils/formatRelativeTime.js";
import ConversationMenu from "./ConversationMenu.jsx";

export default function ConversationItem({
  conversation,
  isActive,
  isRenaming,
  isDeleting,
  onSelect,
  onRename,
  onDelete,
}) {
  return (
    <div
      className={`group flex items-start gap-2 rounded-lg border-l-2 px-2 py-2 transition ${
        isActive
          ? "border-brand-600 bg-brand-50 text-brand-900"
          : "border-transparent text-slate-700 hover:bg-slate-100"
      }`}
    >
      <button
        type="button"
        onClick={() => onSelect(conversation.id)}
        className="flex min-w-0 flex-1 items-start gap-2 text-left"
      >
        <MessageSquare
          className={`mt-0.5 h-3.5 w-3.5 shrink-0 ${
            isActive ? "text-brand-600" : "text-slate-400"
          }`}
        />
        <span className="min-w-0 flex-1">
          <span
            className={`block truncate text-sm ${
              isActive ? "font-semibold" : "font-medium"
            }`}
          >
            {conversation.title}
          </span>
          <span className="mt-0.5 block text-[11px] text-slate-500">
            {formatRelativeTime(conversation.last_message_at || conversation.updated_at)}
          </span>
        </span>
      </button>

      <ConversationMenu
        onRename={onRename}
        onDelete={onDelete}
        disabled={isRenaming || isDeleting}
      />
    </div>
  );
}
