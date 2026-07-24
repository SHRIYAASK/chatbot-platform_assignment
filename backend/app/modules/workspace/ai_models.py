"""Default AI model names for new workspace projects."""

from app.core.config import settings


def get_default_primary_model() -> str:
    return settings.PRIMARY_MODEL


def get_default_fallback_model() -> str:
    return settings.FALLBACK_MODEL
