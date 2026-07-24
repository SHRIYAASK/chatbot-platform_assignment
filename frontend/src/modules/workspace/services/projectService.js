import api from "../../../shared/api/axios.js";

export async function fetchProjects() {
  const response = await api.get("/projects");
  return response.data;
}

export async function fetchProjectById(projectId) {
  const response = await api.get(`/projects/${projectId}`);
  return response.data;
}

export async function createProject(payload) {
  const response = await api.post("/projects", payload);
  return response.data;
}

export async function updateProject(projectId, payload) {
  const response = await api.put(`/projects/${projectId}`, payload);
  return response.data;
}

export async function deleteProject(projectId) {
  await api.delete(`/projects/${projectId}`);
}
