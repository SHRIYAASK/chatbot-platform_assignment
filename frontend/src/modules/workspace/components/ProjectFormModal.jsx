import { useEffect, useMemo, useState } from "react";
import Button from "../../../shared/components/Button.jsx";
import Input from "../../../shared/components/Input.jsx";
import Modal from "../../../shared/components/Modal.jsx";
import { mapApiError, mapNetworkError } from "../../../shared/utils/apiError.js";
import { rewriteProjectDescription } from "../services/projectService.js";
import { validateProjectForm } from "../utils/validation.js";

const emptyForm = { title: "", description: "" };

function isDescriptionValid(description) {
  const trimmed = description.trim();
  return trimmed.length >= 10 && trimmed.length <= 500;
}

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
  const [rewritePreview, setRewritePreview] = useState(null);
  const [rewriting, setRewriting] = useState(false);
  const [rewriteError, setRewriteError] = useState("");

  useEffect(() => {
    if (isOpen) {
      setForm({
        title: initialProject?.title || "",
        description: initialProject?.description || "",
      });
      setErrors({});
      setRewritePreview(null);
      setRewriting(false);
      setRewriteError("");
    }
  }, [isOpen, initialProject]);

  const validation = useMemo(() => validateProjectForm(form), [form]);
  const canEnhance = isDescriptionValid(form.description) && !rewriting;

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
    setErrors((current) => ({ ...current, [name]: "" }));
  };

  const handleDescriptionChange = (event) => {
    const value = event.target.value;
    setForm((current) => ({ ...current, description: value }));
    setErrors((current) => ({ ...current, description: "" }));

    if (rewritePreview && value.trim() !== rewritePreview.sourceSnapshot) {
      setRewritePreview(null);
      setRewriteError("");
    }
  };

  const handleEnhance = async () => {
    const sourceSnapshot = form.description.trim();
    if (!isDescriptionValid(sourceSnapshot)) {
      return;
    }

    setRewriting(true);
    setRewriteError("");
    setRewritePreview(null);

    try {
      const data = await rewriteProjectDescription(sourceSnapshot);
      setRewritePreview({
        text: data.rewritten_description,
        sourceSnapshot,
      });
    } catch (error) {
      const message = error.response
        ? mapApiError(
            error.response.status,
            error.response.data?.detail,
            "Failed to enhance description."
          )
        : mapNetworkError(error, "Failed to enhance description.");
      setRewriteError(message);
    } finally {
      setRewriting(false);
    }
  };

  const handleUseRewrite = () => {
    if (!rewritePreview) {
      return;
    }

    setForm((current) => ({
      ...current,
      description: rewritePreview.text.trim(),
    }));
    setErrors((current) => ({ ...current, description: "" }));
    setRewritePreview(null);
    setRewriteError("");
  };

  const handleKeepOriginal = () => {
    setRewritePreview(null);
    setRewriteError("");
  };

  const handlePreviewChange = (event) => {
    const value = event.target.value;
    setRewritePreview((current) =>
      current ? { ...current, text: value } : current
    );
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
        <div className="space-y-2">
          <div className="space-y-1">
            <label htmlFor="description" className="block text-sm font-medium text-slate-700">
              Project Description *
            </label>
            <textarea
              id="description"
              name="description"
              value={form.description}
              onChange={handleDescriptionChange}
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
          <Button
            type="button"
            variant="secondary"
            disabled={!canEnhance}
            onClick={handleEnhance}
          >
            {rewriting ? "Enhancing..." : "Enhance with AI"}
          </Button>
          {rewriteError ? (
            <p className="text-sm text-red-600">{rewriteError}</p>
          ) : null}
        </div>

        {rewritePreview ? (
          <div className="space-y-3 rounded-lg border border-brand-200 bg-brand-50/40 p-4">
            <p className="text-sm font-medium text-slate-800">AI-rewritten version</p>
            <textarea
              value={rewritePreview.text}
              onChange={handlePreviewChange}
              rows={4}
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
            />
            <div className="flex flex-wrap gap-2">
              <Button type="button" onClick={handleUseRewrite}>
                Use this version
              </Button>
              <Button type="button" variant="secondary" onClick={handleKeepOriginal}>
                Keep my original
              </Button>
            </div>
          </div>
        ) : null}
      </form>
    </Modal>
  );
}
