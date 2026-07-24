import { useCallback, useEffect, useState } from "react";
import { useToast } from "../../../shared/hooks/useToast.jsx";
import { mapApiError, mapNetworkError } from "../../../shared/utils/apiError.js";
import {
  createProject,
  deleteProject,
  fetchProjects,
  updateProject,
} from "../services/projectService.js";

export function useProjects() {
  const { showError, showSuccess } = useToast();
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadProjects = useCallback(async () => {
    setLoading(true);
    try {
      const data = await fetchProjects();
      setProjects(data.projects || []);
    } catch (error) {
      showError(mapNetworkError(error, "Failed to load projects."));
    } finally {
      setLoading(false);
    }
  }, [showError]);

  useEffect(() => {
    loadProjects();
  }, [loadProjects]);

  const handleCreate = async (payload) => {
    try {
      const project = await createProject(payload);
      setProjects((current) => [project, ...current]);
      showSuccess("Project created successfully.");
      return project;
    } catch (error) {
      showError(mapApiError(error.response?.status, error.response?.data?.detail, "Failed to create project."));
      throw error;
    }
  };

  const handleUpdate = async (projectId, payload) => {
    try {
      const project = await updateProject(projectId, payload);
      setProjects((current) =>
        current.map((item) =>
          item.id === projectId ? { ...project, summary: item.summary ?? project.summary } : item
        )
      );
      showSuccess("Project updated successfully.");
      return project;
    } catch (error) {
      showError(mapApiError(error.response?.status, error.response?.data?.detail, "Failed to update project."));
      throw error;
    }
  };

  const handleDelete = async (projectId) => {
    try {
      await deleteProject(projectId);
      setProjects((current) => current.filter((item) => item.id !== projectId));
      showSuccess("Project deleted successfully.");
    } catch (error) {
      showError(mapApiError(error.response?.status, error.response?.data?.detail, "Failed to delete project."));
      throw error;
    }
  };

  return {
    projects,
    loading,
    reloadProjects: loadProjects,
    createProject: handleCreate,
    updateProject: handleUpdate,
    deleteProject: handleDelete,
  };
}
