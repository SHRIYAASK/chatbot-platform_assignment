from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.modules.voice.services.service_token import (
    VoiceServiceContext,
    verify_voice_service_token,
)

service_security = HTTPBearer()


@dataclass(frozen=True)
class VerifiedVoiceServiceContext:
    context: VoiceServiceContext


def get_voice_service_context(
    credentials: HTTPAuthorizationCredentials = Depends(service_security),
) -> VoiceServiceContext:
    try:
        return verify_voice_service_token(credentials.credentials)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
