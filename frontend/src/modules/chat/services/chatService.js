import api from "../../../shared/api/axios.js";

const DEFAULT_LIMIT = 20;

export async function fetchMessages(
  projectId,
  conversationId,
  { cursor, limit = DEFAULT_LIMIT, signal } = {},
) {
  const params = { limit };
  if (cursor) {
    params.cursor = cursor;
  }

  const response = await api.get(
    `/projects/${projectId}/conversations/${conversationId}/messages`,
    { params, signal },
  );
  return response.data;
}

export async function sendMessage(projectId, conversationId, content, { signal } = {}) {
  const response = await api.post(
    `/projects/${projectId}/conversations/${conversationId}/messages`,
    { content },
    { signal },
  );
  return response.data;
}

export async function fetchChatProject(projectId) {
  const response = await api.get(`/projects/${projectId}`);
  return response.data;
}

export { DEFAULT_LIMIT as CHAT_PAGE_SIZE };
