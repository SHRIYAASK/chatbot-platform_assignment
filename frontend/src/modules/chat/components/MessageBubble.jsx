import { memo } from "react";
import MarkdownRenderer from "../../../shared/components/MarkdownRenderer/MarkdownRenderer.jsx";

function MessageBubble({ message }) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`rounded-2xl px-4 py-3 text-sm shadow-sm ${
          isUser
            ? "max-w-[85%] bg-brand-600 text-white"
            : "w-full max-w-[min(100%,800px)] border border-slate-200 bg-white text-slate-800"
        }`}
      >
        {isUser ? (
          <p className="whitespace-pre-wrap break-words leading-relaxed">{message.content}</p>
        ) : (
          <MarkdownRenderer content={message.content} />
        )}
        {!isUser && message.model_used ? (
          <p className="mt-3 border-t border-slate-100 pt-2 text-[11px] text-slate-500">
            via {message.model_used}
          </p>
        ) : null}
      </div>
    </div>
  );
}

export default memo(MessageBubble);
