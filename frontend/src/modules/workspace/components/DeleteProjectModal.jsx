import { useState } from "react";
import Button from "../../../shared/components/Button.jsx";
import Modal from "../../../shared/components/Modal.jsx";

export default function DeleteProjectModal({ isOpen, project, onClose, onConfirm }) {
  const [submitting, setSubmitting] = useState(false);

  const handleDelete = async () => {
    setSubmitting(true);
    try {
      await onConfirm(project.id);
      onClose();
    } catch {
      // Errors are handled by the parent hook toast.
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      title="Delete Project"
      onClose={onClose}
      footer={
        <>
          <Button variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button variant="danger" onClick={handleDelete} disabled={submitting}>
            {submitting ? "Deleting..." : "Delete Project"}
          </Button>
        </>
      }
    >
      <p className="text-sm text-slate-600">
        Are you sure you want to delete{" "}
        <span className="font-semibold text-slate-900">{project?.title}</span>?
        This action cannot be undone.
      </p>
    </Modal>
  );
}
