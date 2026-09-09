import api from "../../../shared/api/axios.js";

export async function fetchVoiceToken(projectId, conversationId) {
  const response = await api.post(
    `/projects/${projectId}/conversations/${conversationId}/voice-token`,
  );
  return response.data;
}
