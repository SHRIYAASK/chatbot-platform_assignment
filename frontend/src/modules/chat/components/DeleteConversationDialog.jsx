import Button from "../../../shared/components/Button.jsx";
import Modal from "../../../shared/components/Modal.jsx";

export default function DeleteConversationDialog({
  isOpen,
  conversation,
  submitting,
  onClose,
  onConfirm,
}) {
  const handleDelete = async () => {
    const success = await onConfirm(conversation.id);
    if (success) {
      onClose();
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      title="Delete Conversation"
      onClose={onClose}
      footer={
        <>
          <Button variant="secondary" onClick={onClose} disabled={submitting}>
            Cancel
          </Button>
          <Button variant="danger" onClick={handleDelete} disabled={submitting}>
            {submitting ? "Deleting..." : "Delete"}
          </Button>
        </>
      }
    >
      <p className="text-sm text-slate-600">
        Are you sure you want to delete{" "}
        <span className="font-semibold text-slate-900">"{conversation?.title}"</span>?
        This action cannot be undone.
      </p>
    </Modal>
  );
}
