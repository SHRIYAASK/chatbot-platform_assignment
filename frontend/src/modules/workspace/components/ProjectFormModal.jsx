import { useEffect, useMemo, useState } from "react";
import Button from "../../../shared/components/Button.jsx";
import Input from "../../../shared/components/Input.jsx";
import Modal from "../../../shared/components/Modal.jsx";
import { validateProjectForm } from "../utils/validation.js";

const emptyForm = { title: "", description: "" };

export default function ProjectFormModal({
  isOpen,
  mode = "create",
  initialProject = null,
  onClose,
  onSubmit,
}) {
  const [form, setForm] = useState(emptyForm);
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setForm({
        title: initialProject?.title || "",
        description: initialProject?.description || "",
      });
      setErrors({});
    }
  }, [isOpen, initialProject]);

  const validation = useMemo(() => validateProjectForm(form), [form]);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
    setErrors((current) => ({ ...current, [name]: "" }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    const result = validateProjectForm(form);
    setErrors(result.errors);
    if (!result.isValid) {
      return;
    }

    setSubmitting(true);
    try {
      await onSubmit(result.payload);
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
      title={mode === "create" ? "Create AI Agent" : "Edit AI Agent"}
      onClose={onClose}
      footer={
        <>
          <Button variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button
            type="submit"
            form="project-form"
            disabled={submitting || !validation.isValid}
          >
            {submitting
              ? "Saving..."
              : mode === "create"
                ? "Create Project"
                : "Save Changes"}
          </Button>
        </>
      }
    >
      <form id="project-form" className="space-y-4" onSubmit={handleSubmit}>
        <Input
          label="Project Title *"
          id="title"
          name="title"
          value={form.title}
          onChange={handleChange}
          placeholder="Python Tutor"
          error={errors.title}
          required
        />
        <div className="space-y-1">
          <label htmlFor="description" className="block text-sm font-medium text-slate-700">
            Project Description *
          </label>
          <textarea
            id="description"
            name="description"
            value={form.description}
            onChange={handleChange}
            rows={4}
            placeholder="Describe what this AI assistant will do."
            className={`w-full rounded-lg border px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-brand-500 ${
              errors.description ? "border-red-500" : "border-slate-300"
            }`}
            required
          />
          {errors.description ? (
            <p className="text-sm text-red-600">{errors.description}</p>
          ) : null}
        </div>
      </form>
    </Modal>
  );
}
