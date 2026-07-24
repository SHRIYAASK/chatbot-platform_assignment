import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useToast } from "../../../shared/hooks/useToast.jsx";
import { fetchProjectById } from "../services/projectService.js";

export function useProject(projectId) {
  const navigate = useNavigate();
  const { showError } = useToast();
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadProject = useCallback(async () => {
    setLoading(true);
    try {
      const data = await fetchProjectById(projectId);
      setProject(data);
    } catch (error) {
      const status = error.response?.status;
      if (status === 404) {
        showError("Project not found.");
      } else if (status === 403) {
        showError("You do not have permission to access this project.");
      } else if (status === 401) {
        showError("Unauthorized. Please log in again.");
      } else {
        showError(error.response?.data?.detail || "Failed to load project.");
      }
      navigate("/dashboard");
    } finally {
      setLoading(false);
    }
  }, [projectId, navigate, showError]);

  useEffect(() => {
    loadProject();
  }, [loadProject]);

  return { project, loading, reloadProject: loadProject };
}
