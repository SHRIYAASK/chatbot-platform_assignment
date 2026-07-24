"""Resolve project model names to valid Groq model identifiers."""

from app.core.config import settings

# Legacy placeholder names stored before Groq integration was finalized.
LEGACY_MODEL_MAP: dict[str, str] = {
    "grok-opus-4-120b": settings.PRIMARY_MODEL,
    "llama-3.3-70b": settings.FALLBACK_MODEL,
}


def resolve_project_models(primary_model: str, fallback_model: str) -> tuple[str, str]:
    """Map legacy/invalid stored models to configured Groq models."""
    primary = LEGACY_MODEL_MAP.get(primary_model, primary_model) or settings.PRIMARY_MODEL
    fallback = LEGACY_MODEL_MAP.get(fallback_model, fallback_model) or settings.FALLBACK_MODEL
    return primary, fallback
