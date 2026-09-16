export const PRODUCT_NAME = "Synora";

export const TAGLINE = "Multi-Tenant AI Assistant & Knowledge Platform";

export const GITHUB_REPO_URL =
  import.meta.env.VITE_GITHUB_REPO_URL?.trim() ||
  "https://github.com/SHRIYAASK/chatbot-platform_assignment";

export const LANDING_FEATURES = [
  {
    title: "Secure workspaces",
    detail: "JWT authentication with per-user data isolation across projects and chats.",
  },
  {
    title: "Custom AI projects",
    detail: "Create assistants with your own system prompt and Groq model settings.",
  },
  {
    title: "Enhance with AI",
    detail: "Rewrite project instructions, preview, and confirm before anything is saved.",
  },
  {
    title: "Threaded conversations",
    detail: "Keep persistent chat history for every project conversation.",
  },
  {
    title: "Knowledge & RAG",
    detail: "Upload PDF, TXT, MD, JSON, or DOCX files and retrieve grounded answers.",
  },
  {
    title: "Document-grounded replies",
    detail: "Vector search over your files so answers stay tied to uploaded sources.",
  },
  {
    title: "Guardrails",
    detail: "Configurable input and output moderation before content reaches the user.",
  },
  {
    title: "Voice conversations",
    detail: "Optional LiveKit + Sarvam calls that share the same chat pipeline as text.",
  },
];
