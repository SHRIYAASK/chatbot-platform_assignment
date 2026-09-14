import json
import logging
import os
import re
import sys
from dataclasses import dataclass
from typing import Any, AsyncIterable

# Register all SQLAlchemy models in worker process so mappers are fully initialized
from app.modules.authentication.models.user import User  # noqa: F401
from app.modules.chat.models.chat_message import ChatMessage  # noqa: F401
from app.modules.chat.models.conversation import Conversation  # noqa: F401
from app.modules.chat.models.document import Document  # noqa: F401
from app.modules.chat.models.document_chunk import DocumentChunk  # noqa: F401
from app.modules.file_upload.models.file import ProjectFile  # noqa: F401
from app.modules.prompt_management.models.prompt import Prompt  # noqa: F401
from app.modules.workspace.models.project import Project  # noqa: F401
from app.shared.guardrails.moderation.models import ModerationEvent  # noqa: F401

from livekit import agents
from livekit.agents import Agent, AgentServer, AgentSession, ModelSettings, inference, llm, room_io
from livekit.agents.llm import LLM, LLMStream
from livekit.agents.types import DEFAULT_API_CONNECT_OPTIONS, APIConnectOptions, NOT_GIVEN, NotGivenOr
from livekit.plugins import sarvam

from app.core.config import settings
from app.modules.voice.services.voice_token_service import VOICE_AGENT_NAME
from app.modules.voice.worker.backend_client import stream_chat

logger = logging.getLogger("voice-agent")
if not logger.handlers:
    _handler = logging.StreamHandler(sys.stdout)
    _handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] [voice-agent] %(message)s")
    )
    logger.addHandler(_handler)
logger.setLevel(logging.INFO)

DEFAULT_LANGUAGE = "en-IN"
INDIC_SCRIPT = re.compile(r"[\u0900-\u097F\u0980-\u09FF\u0A00-\u0A7F\u0A80-\u0AFF]")


@dataclass(frozen=True)
class BackendContext:
    backend_url: str
    project_id: int
    conversation_id: int
    service_token: str


class _EmptyLLMStream(LLMStream):
    async def _run(self) -> None:
        return


class PassthroughLLM(LLM):
    """Placeholder so AgentSession will call llm_node. Inference goes to the backend."""

    @property
    def model(self) -> str:
        return "chat-service"

    @property
    def provider(self) -> str:
        return "chatbot-platform"

    def chat(
        self,
        *,
        chat_ctx: llm.ChatContext,
        tools: list | None = None,
        conn_options: APIConnectOptions = DEFAULT_API_CONNECT_OPTIONS,
        parallel_tool_calls: NotGivenOr[bool] = NOT_GIVEN,
        tool_choice=None,
        extra_kwargs=None,
    ) -> LLMStream:
        return _EmptyLLMStream(
            self,
            chat_ctx=chat_ctx,
            tools=tools or [],
            conn_options=conn_options,
        )


def _detect_language(text: str) -> str:
    if INDIC_SCRIPT.search(text):
        return "hi-IN"
    return DEFAULT_LANGUAGE


def _try_parse_metadata(raw: str | None) -> BackendContext | None:
    if not raw or not raw.strip():
        return None
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return None
    try:
        return BackendContext(
            # Always use the runtime URL — token metadata may carry a stale port.
            backend_url=settings.VOICE_API_BASE_URL.rstrip("/"),
            project_id=int(payload["project_id"]),
            conversation_id=int(payload["conversation_id"]),
            service_token=str(payload["service_token"]),
        )
    except (KeyError, TypeError, ValueError):
        return None


def _parse_metadata(ctx: agents.JobContext) -> BackendContext:
    candidates = [
        getattr(ctx.job, "metadata", None),
        ctx.room.metadata,
    ]
    for participant in ctx.room.remote_participants.values():
        candidates.append(participant.metadata)

    for raw in candidates:
        parsed = _try_parse_metadata(raw)
        if parsed:
            return parsed

    # Fallback: recover context directly from room name (e.g. conv-5)
    room_name = getattr(ctx.room, "name", None) or ""
    if room_name.startswith("conv-"):
        try:
            conversation_id = int(room_name.replace("conv-", ""))
            from app.core.database import SessionLocal
            from app.modules.chat.models.conversation import Conversation
            from app.modules.voice.services.service_token import create_voice_service_token

            with SessionLocal() as db:
                conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
                if conv:
                    service_token = create_voice_service_token(
                        user_id=conv.user_id,
                        project_id=conv.project_id,
                        conversation_id=conv.id,
                    )
                    logger.info(
                        "Recovered voice context from room %s: project=%s conversation=%s",
                        room_name,
                        conv.project_id,
                        conv.id,
                    )
                    return BackendContext(
                        backend_url=settings.VOICE_API_BASE_URL.rstrip("/"),
                        project_id=conv.project_id,
                        conversation_id=conv.id,
                        service_token=service_token,
                    )
        except Exception:
            logger.exception("Failed to recover conversation context from room name %s", room_name)

    raise ValueError(
        "Voice agent metadata is missing. "
        "Join via POST /voice-token so the room includes project/conversation context."
    )


def _latest_user_message(chat_ctx: llm.ChatContext) -> str | None:
    for item in reversed(chat_ctx.items):
        if getattr(item, "type", None) == "message" and getattr(item, "role", None) == "user":
            text = item.text_content
            if text and text.strip():
                return text.strip()
    return None


def _get_runtime_backend_url() -> str:
    port = (os.environ.get("PORT") or "8002").strip() or "8002"
    url = (os.environ.get("VOICE_API_BASE_URL") or "").strip()
    if "${PORT}" in url or "$PORT" in url:
        return url.replace("${PORT}", port).replace("$PORT", port).rstrip("/")
    if not url or "127.0.0.1" in url or "localhost" in url:
        return f"http://127.0.0.1:{port}"
    return url.rstrip("/")


class BackendVoiceAgent(Agent):
    def __init__(self, backend_ctx: BackendContext, tts: sarvam.TTS, passthrough_llm: LLM) -> None:
        super().__init__(
            instructions=(
                "You are a helpful voice assistant. "
                "Keep responses concise and conversational."
            ),
            llm=passthrough_llm,
            tts=tts,
        )
        self._backend_ctx = backend_ctx
        self._tts = tts

    async def llm_node(
        self,
        chat_ctx: llm.ChatContext,
        tools: list,
        model_settings: ModelSettings,
    ) -> AsyncIterable[str | llm.ChatChunk]:
        user_message = _latest_user_message(chat_ctx)
        if not user_message:
            logger.warning("llm_node invoked without a user transcript")
            return

        language = _detect_language(user_message)
        try:
            self._tts.update_options(target_language_code=language)
        except Exception:
            logger.exception("Failed to update TTS language to %s", language)

        logger.info(
            "Streaming chat for conversation=%s: %s",
            self._backend_ctx.conversation_id,
            user_message[:80],
        )

        backend_url = _get_runtime_backend_url()
        try:
            async for chunk in stream_chat(
                backend_url=backend_url,
                project_id=self._backend_ctx.project_id,
                conversation_id=self._backend_ctx.conversation_id,
                service_token=self._backend_ctx.service_token,
                content=user_message,
            ):
                if chunk:
                    yield chunk
            return
        except Exception:
            logger.warning(
                "HTTP stream_chat failed for conversation=%s backend=%s; falling back to in-process ChatService",
                self._backend_ctx.conversation_id,
                backend_url,
            )

        # In-process direct fallback
        try:
            from app.modules.chat.services.chat_service import ChatService
            from app.modules.voice.services.service_token import verify_voice_service_token

            context = verify_voice_service_token(self._backend_ctx.service_token)
            async for chunk in ChatService.stream_message(
                user_id=context.user_id,
                project_id=self._backend_ctx.project_id,
                conversation_id=self._backend_ctx.conversation_id,
                content=user_message,
            ):
                if chunk:
                    yield chunk
            return
        except Exception:
            logger.exception(
                "Direct ChatService stream fallback also failed for conversation=%s",
                self._backend_ctx.conversation_id,
            )
            yield "Sorry, I could not generate a response. Please try again."


def _agent_server_options() -> dict[str, Any]:
    """Ensure minimal RAM usage so the worker stays well within 512MB container limits."""
    return {
        "num_idle_processes": 0,
        "load_threshold": 0.99,
        "initialize_process_timeout": 120.0,
    }


server = AgentServer(**_agent_server_options())


@server.rtc_session(agent_name=VOICE_AGENT_NAME)
async def entrypoint(ctx: agents.JobContext):
    job_id = getattr(ctx.job, "id", None) or getattr(ctx.job, "job_id", None)
    room_name = getattr(ctx.room, "name", None) or "unknown"
    logger.info(
        "Voice agent job received job_id=%s room=%s",
        job_id,
        room_name,
    )
    await ctx.connect()
    backend_ctx = _parse_metadata(ctx)
    logger.info(
        "Joining voice room for project=%s conversation=%s backend=%s",
        backend_ctx.project_id,
        backend_ctx.conversation_id,
        backend_ctx.backend_url,
    )

    passthrough_llm = PassthroughLLM()
    tts = sarvam.TTS(
        model="bulbul:v3",
        target_language_code=DEFAULT_LANGUAGE,
        speaker="shubh",
        api_key=settings.SARVAM_API_KEY,
    )
    stt = sarvam.STT(
        model="saarika:v2.5",
        language=DEFAULT_LANGUAGE,
        api_key=settings.SARVAM_API_KEY,
    )
    vad = inference.VAD(
        model="silero",
        min_speech_duration=0.05,
        min_silence_duration=0.4,
        prefix_padding_duration=0.3,
        activation_threshold=0.5,
    )

    session = AgentSession(
        stt=stt,
        tts=tts,
        llm=passthrough_llm,
        vad=vad,
        turn_handling={
            "turn_detection": "stt",
            "endpointing": {"min_delay": 0.6, "max_delay": 3.0},
        },
    )

    await session.start(
        room=ctx.room,
        agent=BackendVoiceAgent(backend_ctx, tts, passthrough_llm),
        room_options=room_io.RoomOptions(),
    )
