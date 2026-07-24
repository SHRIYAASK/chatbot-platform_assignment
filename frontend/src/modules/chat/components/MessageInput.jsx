import { useEffect, useRef, useState } from "react";
import Button from "../../../shared/components/Button.jsx";

export default function MessageInput({
  onSend,
  onStop,
  isGenerating,
  disabled,
  focusInputToken = 0,
}) {
  const [value, setValue] = useState("");
  const textareaRef = useRef(null);

  useEffect(() => {
    if (focusInputToken > 0) {
      textareaRef.current?.focus();
    }
  }, [focusInputToken]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    const trimmed = value.trim();
    if (!trimmed || disabled || isGenerating) {
      return;
    }

    const sent = await onSend(trimmed);
    if (sent) {
      setValue("");
    }
  };

  const handleStop = (event) => {
    event.preventDefault();
    onStop?.();
  };

  return (
    <form
      onSubmit={isGenerating ? handleStop : handleSubmit}
      className="border-t border-slate-200 bg-white px-4 py-4 sm:px-6"
    >
      <div className="flex gap-3">
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(event) => setValue(event.target.value)}
          rows={2}
          placeholder={isGenerating ? "Generating response..." : "Type your message..."}
          disabled={disabled}
          className="min-h-[48px] flex-1 resize-none rounded-xl border border-slate-300 px-4 py-3 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-brand-500 disabled:bg-slate-100"
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey && !isGenerating) {
              event.preventDefault();
              handleSubmit(event);
            }
          }}
        />
        {isGenerating ? (
          <Button type="submit" variant="danger" className="self-end whitespace-nowrap">
            Stop Generating
          </Button>
        ) : (
          <Button
            type="submit"
            disabled={disabled || !value.trim()}
            className="self-end"
          >
            Send
          </Button>
        )}
      </div>
    </form>
  );
}
