from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.core.config import settings


VOICE_SERVICE_TOKEN_TYPE = "voice_service"


@dataclass(frozen=True)
class VoiceServiceContext:
    user_id: int
    project_id: int
    conversation_id: int


def create_voice_service_token(
    *,
    user_id: int,
    project_id: int,
    conversation_id: int,
) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.VOICE_SERVICE_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": str(user_id),
        "type": VOICE_SERVICE_TOKEN_TYPE,
        "project_id": project_id,
        "conversation_id": conversation_id,
        "exp": expire,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_voice_service_token(token: str) -> VoiceServiceContext:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
    except JWTError as exc:
        raise ValueError("Invalid voice service token.") from exc

    if payload.get("type") != VOICE_SERVICE_TOKEN_TYPE:
        raise ValueError("Invalid voice service token type.")

    try:
        user_id = int(payload["sub"])
        project_id = int(payload["project_id"])
        conversation_id = int(payload["conversation_id"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("Voice service token payload is incomplete.") from exc

    return VoiceServiceContext(
        user_id=user_id,
        project_id=project_id,
        conversation_id=conversation_id,
    )
