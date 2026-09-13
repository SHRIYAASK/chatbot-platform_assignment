import json
import logging
import os
import re
from dataclasses import dataclass
from typing import Any, AsyncIterable

from livekit import agents
from livekit.agents import Agent, AgentServer, AgentSession, ModelSettings, inference, llm, room_io
from livekit.agents.llm import LLM, LLMStream
from livekit.agents.types import DEFAULT_API_CONNECT_OPTIONS, APIConnectOptions, NOT_GIVEN, NotGivenOr
from livekit.plugins import sarvam

from app.core.config import settings
from app.modules.voice.services.voice_token_service import VOICE_AGENT_NAME
from app.modules.voice.worker.backend_client import stream_chat

logger = logging.getLogger("voice-agent")

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

        try:
            async for chunk in stream_chat(
                backend_url=self._backend_ctx.backend_url,
                project_id=self._backend_ctx.project_id,
                conversation_id=self._backend_ctx.conversation_id,
                service_token=self._backend_ctx.service_token,
                content=user_message,
            ):
                if chunk:
                    yield chunk
        except Exception:
            logger.exception(
                "Voice backend stream failed for conversation=%s backend=%s",
                self._backend_ctx.conversation_id,
                self._backend_ctx.backend_url,
            )
            yield "Sorry, I could not generate a response. Please try again."


def _agent_server_options() -> dict[str, Any]:
    """Render starter instances have little CPU/RAM; default LiveKit settings mark the worker full."""
    if os.environ.get("RENDER") or os.environ.get("VOICE_AGENT_LOW_RESOURCES", "").lower() == "true":
        return {
            "num_idle_processes": 0,
            "load_threshold": 0.99,
            "initialize_process_timeout": 120.0,
        }
    return {}


server = AgentServer(**_agent_server_options())


@server.rtc_session(agent_name=VOICE_AGENT_NAME)
async def entrypoint(ctx: agents.JobContext):
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
    )
    stt = sarvam.STT(
        model="saaras:v3",
        mode="transcribe",
        language=DEFAULT_LANGUAGE,
        flush_signal=True,
        high_vad_sensitivity=True,
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
