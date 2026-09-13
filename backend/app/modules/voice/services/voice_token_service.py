import json

from livekit import api

from app.core.config import settings
from app.modules.authentication.models.user import User
from app.modules.voice.services.service_token import create_voice_service_token

VOICE_AGENT_NAME = "chatbot-voice-agent"


class VoiceNotConfiguredError(Exception):
    """Raised when LiveKit credentials are missing."""


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
    def mint_token(
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
            .with_room_config(
                api.RoomConfiguration(
                    agents=[
                        api.RoomAgentDispatch(
                            agent_name=VOICE_AGENT_NAME,
                            metadata=metadata_json,
                        )
                    ],
                )
            )
        )

        return settings.LIVEKIT_URL.rstrip("/"), access_token.to_jwt(), room_name
