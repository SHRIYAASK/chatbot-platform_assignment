import { useEffect, useState } from "react";
import Button from "../../../shared/components/Button.jsx";
import Modal from "../../../shared/components/Modal.jsx";

const MIN_TITLE_LENGTH = 3;
const MAX_TITLE_LENGTH = 60;

function validateTitle(value) {
  const trimmed = value.trim();
  if (!trimmed) {
    return "Title is required.";
  }
  if (trimmed.length < MIN_TITLE_LENGTH) {
    return `Title must be at least ${MIN_TITLE_LENGTH} characters long.`;
  }
  if (trimmed.length > MAX_TITLE_LENGTH) {
    return `Title must not exceed ${MAX_TITLE_LENGTH} characters.`;
  }
  return "";
}

export default function RenameConversationDialog({
  isOpen,
  conversation,
  submitting,
  onClose,
  onConfirm,
}) {
  const [title, setTitle] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    if (isOpen && conversation) {
      setTitle(conversation.title || "");
      setError("");
    }
  }, [isOpen, conversation]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    const validationError = validateTitle(title);
    if (validationError) {
      setError(validationError);
      return;
    }

    const success = await onConfirm(conversation.id, title.trim());
    if (success) {
      onClose();
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      title="Rename Conversation"
      onClose={onClose}
      footer={
        <>
          <Button variant="secondary" onClick={onClose} disabled={submitting}>
            Cancel
          </Button>
          <Button onClick={handleSubmit} disabled={submitting}>
            {submitting ? "Saving..." : "Save"}
          </Button>
        </>
      }
    >
      <form onSubmit={handleSubmit} className="space-y-3">
        <div>
          <label htmlFor="conversation-title" className="mb-1 block text-sm font-medium text-slate-700">
            Conversation title
          </label>
          <input
            id="conversation-title"
            type="text"
            value={title}
            maxLength={MAX_TITLE_LENGTH}
            onChange={(event) => {
              setTitle(event.target.value);
              if (error) {
                setError("");
              }
            }}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
            autoFocus
          />
          {error ? <p className="mt-1 text-xs text-red-600">{error}</p> : null}
        </div>
      </form>
    </Modal>
  );
}
