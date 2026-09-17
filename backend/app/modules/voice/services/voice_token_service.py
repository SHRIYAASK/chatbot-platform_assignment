import json
import logging

from livekit import api

from app.core.config import settings
from app.modules.authentication.models.user import User
from app.modules.voice.services.service_token import create_voice_service_token

logger = logging.getLogger(__name__)

VOICE_AGENT_NAME = "chatbot-voice-agent"


class VoiceNotConfiguredError(Exception):
    """Raised when LiveKit credentials are missing."""


class VoiceAgentDispatchError(Exception):
    """Raised when explicit agent dispatch to LiveKit fails."""


class VoiceTokenService:
    @staticmethod
    def is_configured() -> bool:
        return bool(
            settings.LIVEKIT_URL.strip()
            and settings.LIVEKIT_API_KEY.strip()
            and settings.LIVEKIT_API_SECRET.strip()
        )

    @staticmethod
    def room_name(conversation_id: int) -> str:
        return f"conv-{conversation_id}"

    @staticmethod
    async def _dispatch_agent(room_name: str, metadata_json: str) -> None:
        """Dispatch the voice agent every time a user starts a call.

        Token-embedded RoomAgentDispatch only runs when the room is first created;
        explicit dispatch is required when the room already exists (retries).
        """
        try:
            async with api.LiveKitAPI(
                url=settings.LIVEKIT_URL.rstrip("/"),
                api_key=settings.LIVEKIT_API_KEY,
                api_secret=settings.LIVEKIT_API_SECRET,
            ) as lkapi:
                await lkapi.agent_dispatch.create_dispatch(
                    api.CreateAgentDispatchRequest(
                        agent_name=VOICE_AGENT_NAME,
                        room=room_name,
                        metadata=metadata_json,
                    )
                )
        except Exception as exc:
            logger.exception(
                "LiveKit agent dispatch failed for room=%s agent=%s",
                room_name,
                VOICE_AGENT_NAME,
            )
            raise VoiceAgentDispatchError(
                "Could not dispatch the voice agent. Check LiveKit credentials and "
                "that the embedded worker is registered."
            ) from exc

    @staticmethod
    async def mint_token(
        *,
        current_user: User,
        project_id: int,
        conversation_id: int,
    ) -> tuple[str, str, str]:
        if not VoiceTokenService.is_configured():
            raise VoiceNotConfiguredError("LiveKit voice is not configured.")

        service_token = create_voice_service_token(
            user_id=current_user.id,
            project_id=project_id,
            conversation_id=conversation_id,
        )
        room_name = VoiceTokenService.room_name(conversation_id)
        metadata = {
            "project_id": project_id,
            "conversation_id": conversation_id,
            "user_id": current_user.id,
            "service_token": service_token,
            "backend_url": settings.VOICE_API_BASE_URL.rstrip("/"),
        }
        metadata_json = json.dumps(metadata)

        await VoiceTokenService._dispatch_agent(room_name, metadata_json)

        # Dispatch only via create_dispatch above. RoomAgentDispatch on the JWT would
        # spawn a second agent when the room is first created (duplicate transcripts).
        access_token = (
            api.AccessToken(settings.LIVEKIT_API_KEY, settings.LIVEKIT_API_SECRET)
            .with_identity(f"user-{current_user.id}")
            .with_name(current_user.name)
            .with_metadata(metadata_json)
            .with_grants(
                api.VideoGrants(
                    room_join=True,
                    room=room_name,
                    can_publish=True,
                    can_subscribe=True,
                )
            )
        )

        return settings.LIVEKIT_URL.rstrip("/"), access_token.to_jwt(), room_name
