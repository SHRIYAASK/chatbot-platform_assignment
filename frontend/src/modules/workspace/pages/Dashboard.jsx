import { useState } from "react";
import Button from "../../../shared/components/Button.jsx";
import Loader from "../../../shared/components/Loader.jsx";
import { useAuth } from "../../authentication/context/AuthContext.jsx";
import DeleteProjectModal from "../components/DeleteProjectModal.jsx";
import ProjectCard from "../components/ProjectCard/ProjectCard.jsx";
import ProjectFormModal from "../components/ProjectFormModal.jsx";
import { useProjects } from "../hooks/useProjects.js";

export default function Dashboard() {
  const { user } = useAuth();
  const {
    projects,
    loading,
    createProject,
    updateProject,
    deleteProject,
  } = useProjects();

  const [formModal, setFormModal] = useState({ open: false, mode: "create", project: null });
  const [deleteModal, setDeleteModal] = useState({ open: false, project: null });

  const openCreateModal = () => {
    setFormModal({ open: true, mode: "create", project: null });
  };

  const openEditModal = (project) => {
    setFormModal({ open: true, mode: "edit", project });
  };

  const openDeleteModal = (project) => {
    setDeleteModal({ open: true, project });
  };

  const closeFormModal = () => {
    setFormModal({ open: false, mode: "create", project: null });
  };

  const closeDeleteModal = () => {
    setDeleteModal({ open: false, project: null });
  };

  const handleFormSubmit = async (payload) => {
    if (formModal.mode === "create") {
      await createProject(payload);
      return;
    }

    await updateProject(formModal.project.id, payload);
  };

  return (
    <main className="mx-auto max-w-6xl px-4 py-8">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">
            Welcome, {user?.name}
          </h1>
          <p className="mt-2 text-slate-600">
            Create and manage AI chatbot agents for your workspace.
          </p>
        </div>
        <Button onClick={openCreateModal}>+ Create Project</Button>
      </div>

      <section className="mt-8">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-xl font-semibold text-slate-900">Projects</h2>
          <span className="text-sm text-slate-500">
            {projects.length} project{projects.length === 1 ? "" : "s"}
          </span>
        </div>

        {loading ? (
          <Loader label="Loading projects..." />
        ) : projects.length === 0 ? (
          <div className="rounded-xl border border-dashed border-slate-300 bg-white p-10 text-center">
            <h3 className="text-lg font-semibold text-slate-900">No projects yet</h3>
            <p className="mt-2 text-sm text-slate-600">
              Create your first AI assistant project to get started.
            </p>
            <Button className="mt-4" onClick={openCreateModal}>
              Create Project
            </Button>
          </div>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {projects.map((project) => (
              <ProjectCard
                key={project.id}
                project={project}
                onEdit={openEditModal}
                onDelete={openDeleteModal}
              />
            ))}
          </div>
        )}
      </section>

      <ProjectFormModal
        isOpen={formModal.open}
        mode={formModal.mode}
        initialProject={formModal.project}
        onClose={closeFormModal}
        onSubmit={handleFormSubmit}
      />

      <DeleteProjectModal
        isOpen={deleteModal.open}
        project={deleteModal.project}
        onClose={closeDeleteModal}
        onConfirm={deleteProject}
      />
    </main>
  );
}
