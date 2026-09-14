/**
 * Architecture copy and Mermaid diagrams for the Synora landing page.
 * Keep in sync with README.md "Architecture & design" section when updating flows.
 */

export const HLD_SUMMARY = [
  "End users build per-project AI assistants with custom system prompts and optional knowledge documents.",
  "React SPA on Vercel talks to a FastAPI modular monolith on Railway with PostgreSQL + pgvector.",
  "Groq powers chat; Hugging Face embeddings power RAG; LiveKit + Sarvam power optional real-time voice.",
  "An embedded LiveKit worker in the API container streams voice turns through the same ChatService as text.",
];

export const LLD_FRONTEND = [
  { module: "authentication", role: "Login, register, JWT in localStorage, ProtectedRoute" },
  { module: "workspace", role: "Projects dashboard, create/edit, Enhance-with-AI modal" },
  { module: "chat", role: "Conversations, messages, RAG uploads, LiveKit voice (useVoiceCall)" },
];

export const LLD_BACKEND = [
  { module: "authentication", role: "JWT issue/verify, bcrypt, get_current_user dependency" },
  { module: "workspace", role: "Projects CRUD, stateless description rewrite endpoint" },
  { module: "chat", role: "ChatService, conversations, documents, background indexing" },
  { module: "voice", role: "VoiceTokenService + explicit agent dispatch, SSE stream for worker" },
  { module: "shared", role: "RAG retrieval, LLM/Groq client, moderation guardrails" },
];

export const TENANCY_BULLETS = [
  "Every API call carries a Bearer JWT; services resolve user_id from token claims.",
  "Projects, conversations, documents, and chunks are filtered by user_id and project_id.",
  "Vector search never crosses project boundaries.",
];

export const DIAGRAMS = {
  productJourney: {
    title: "Product journey",
    mermaid: `flowchart LR
    A[Register / Login] --> B[Create Project]
    B --> B2[Optional Enhance with AI]
    B2 --> C[Upload Documents]
    C --> D[Chat or Voice]
    D --> E[History Persists]`,
  },
  hld: {
    title: "High-level system",
    mermaid: `flowchart TB
    subgraph Client["Browser"]
        UI[React SPA]
    end
    subgraph Vercel["Vercel"]
        FE[Static build]
    end
    subgraph Railway["Railway"]
        API[FastAPI Docker]
        PG[(PostgreSQL + pgvector)]
        FS[uploads/]
        VA[embedded voice worker]
    end
    subgraph VoiceCloud["Voice optional"]
        LK[LiveKit Cloud]
        SV[Sarvam STT/TTS]
    end
    subgraph External["External AI"]
        Groq[Groq]
        HF[Hugging Face]
    end
    UI --> FE
    FE -->|HTTPS JWT| API
    API --> PG
    API --> FS
    API --> Groq
    API --> HF
    FE -->|WebRTC| LK
    VA -->|RTC| LK
    VA --> SV
    VA -->|HTTP SSE| API`,
  },
  backendLayers: {
    title: "Backend layers",
    mermaid: `flowchart LR
    subgraph Routers
        R1["/auth"]
        R2["/projects"]
        R2b["/projects/description/rewrite"]
        R3["/projects/id/conversations"]
        R4["/projects/id/messages"]
        R5["/projects/id/documents"]
        R6["voice-token and SSE"]
    end
    subgraph Services
        AuthSvc[AuthService]
        ProjSvc[ProjectService]
        RewriteSvc[DescriptionRewriteService]
        ChatSvc[ChatService]
        UploadSvc[UploadService]
        LLMSvc[LLMService]
        RetSvc[RetrievalService]
        VoiceSvc[VoiceTokenService]
    end
    subgraph Shared
        RAG[RAG]
        LLM[Prompt builder]
    end
    R1 --> AuthSvc
    R2 --> ProjSvc
    R2b --> RewriteSvc
    R3 --> ChatSvc
    R4 --> ChatSvc
    R5 --> UploadSvc
    R6 --> VoiceSvc
    R6 --> ChatSvc
    RewriteSvc --> LLMSvc
    ChatSvc --> RetSvc
    ChatSvc --> LLMSvc
    ChatSvc --> LLM
    RetSvc --> RAG
    UploadSvc --> RAG`,
  },
  auth: {
    title: "Authentication",
    mermaid: `sequenceDiagram
    participant User
    participant SPA as React_SPA
    participant API as FastAPI
    participant DB as PostgreSQL
    User->>SPA: Register_or_login
    SPA->>API: POST_auth_register_or_login
    API->>DB: Create_or_verify_user
    API-->>SPA: access_token_JWT
    SPA->>SPA: Store_token_localStorage
    SPA->>API: GET_auth_me_Bearer
    API-->>SPA: User_profile
    Note over SPA,API: Protected routes send Authorization header`,
  },
  chatRag: {
    title: "Chat and RAG",
    mermaid: `sequenceDiagram
    participant UI as Chat_UI
    participant API as ChatService
    participant Mod as Moderation
    participant RAG as RetrievalService
    participant Groq as Groq
    participant DB as PostgreSQL
    UI->>API: POST_message
    API->>Mod: check_input_optional
    API->>RAG: top_k_child_chunks
    RAG->>DB: pgvector_similarity
    RAG-->>API: parent_context
    API->>Groq: layered_prompt
    Groq-->>API: reply
    API->>Mod: check_output_optional
    API->>DB: save_user_and_assistant_messages
    API-->>UI: response`,
  },
  docIndexing: {
    title: "Document indexing",
    mermaid: `sequenceDiagram
    participant UI as Upload_UI
    participant API as DocumentService
    participant BG as BackgroundTasks
    participant HF as HuggingFace
    participant DB as PostgreSQL
    UI->>API: POST_document
    API->>DB: status_processing
    API-->>UI: 201_Created
    API->>BG: extract_chunk_embed
    BG->>HF: embed_texts
    HF-->>BG: vectors
    BG->>DB: document_chunks_ready
    BG->>DB: status_ready`,
  },
  descriptionRewrite: {
    title: "Description rewrite (review-and-confirm)",
    mermaid: `sequenceDiagram
    participant User
    participant Modal as ProjectFormModal
    participant API as POST_description_rewrite
    participant Groq as LLMService
    participant Save as POST_PUT_projects
    User->>Modal: Enhance with AI
    Modal->>API: description only
    API->>Groq: rewrite prompt
    Groq-->>API: rewritten_description
    API-->>Modal: preview panel
    alt Use this version
        User->>Modal: Confirm
        Modal->>Modal: Copy into form.description
    else Keep original
        User->>Modal: Discard preview
    end
    User->>Save: Create or Save Changes
    Save->>Save: Persist confirmed description only`,
  },
  voice: {
    title: "Voice (LiveKit + Sarvam)",
    mermaid: `sequenceDiagram
    participant FE as Browser
    participant API as FastAPI
    participant LK as LiveKit_Cloud
    participant VA as embedded_worker
    participant SV as Sarvam
    FE->>API: POST_voice_token
    API->>LK: AgentDispatch_create_dispatch
    API-->>FE: livekit_url_and_JWT
    FE->>LK: WebRTC_connect_room
    LK->>VA: dispatch_job
    VA->>LK: join_room
    FE->>LK: publish_mic
    LK->>VA: audio
    VA->>SV: STT
    VA->>API: POST_voice_messages_stream_SSE
    API-->>VA: ChatService_stream_deltas
    VA->>SV: TTS
    VA->>LK: agent_audio
    LK->>FE: playback`,
  },
};

export const FLOW_SECTIONS = [
  DIAGRAMS.auth,
  DIAGRAMS.chatRag,
  DIAGRAMS.docIndexing,
  DIAGRAMS.descriptionRewrite,
  DIAGRAMS.voice,
];
