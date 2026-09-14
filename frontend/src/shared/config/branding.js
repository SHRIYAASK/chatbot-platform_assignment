export const PRODUCT_NAME = "Synora";

export const TAGLINE = "Multi-Tenant AI Assistant & Knowledge Platform";

export const ELEVATOR_PITCH =
  "Full-stack platform for personalized AI assistants: custom system prompts, document-based RAG, persistent conversational memory, and real-time WebRTC voice—powered by React, FastAPI, Groq, PostgreSQL/pgvector, and LiveKit + Sarvam.";

export const DEMO_STEPS = [
  {
    title: "Auth & workspace",
    detail: "Register or log in, then create a project with per-user data isolation.",
  },
  {
    title: "Enhance with AI",
    detail: "Draft a short description, rewrite with Groq, preview, and confirm before save.",
  },
  {
    title: "Knowledge & RAG",
    detail: "Upload PDFs or docs, wait for indexing, then ask questions grounded in your files.",
  },
  {
    title: "Voice (optional)",
    detail: "Start a WebRTC call; the embedded worker uses the same ChatService as text chat.",
  },
];

export const TECH_STACK = [
  "React 18",
  "Vite",
  "Tailwind CSS",
  "FastAPI",
  "PostgreSQL",
  "pgvector",
  "Groq",
  "Hugging Face Embeddings",
  "LiveKit",
  "Sarvam STT/TTS",
];
