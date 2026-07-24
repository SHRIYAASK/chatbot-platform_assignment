import api from "../../../shared/api/axios.js";

export async function fetchConversations(projectId, { search, signal } = {}) {
  const params = {};
  if (search?.trim()) {
    params.search = search.trim();
  }

  const response = await api.get(`/projects/${projectId}/conversations`, { params, signal });
  return response.data;
}

export async function createConversation(projectId, { title = "New Chat" } = {}) {
  const response = await api.post(`/projects/${projectId}/conversations`, { title });
  return response.data;
}

export async function updateConversation(projectId, conversationId, { title }) {
  const response = await api.patch(
    `/projects/${projectId}/conversations/${conversationId}`,
    { title },
  );
  return response.data;
}

export async function deleteConversation(projectId, conversationId) {
  await api.delete(`/projects/${projectId}/conversations/${conversationId}`);
}
