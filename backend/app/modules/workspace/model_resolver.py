"""Resolve project model names to valid Groq model identifiers."""

from app.core.config import settings

# Legacy placeholder names stored before Groq integration was finalized.
LEGACY_MODEL_MAP: dict[str, str] = {
    "grok-opus-4-120b": "openai/gpt-oss-120b",
    "gpt-oss-120b": "openai/gpt-oss-120b",
    "llama-3.3-70b": "llama-3.3-70b-versatile",
}


def resolve_project_models(primary_model: str, fallback_model: str) -> tuple[str, str]:
    """Map legacy/invalid stored models to configured Groq models."""
    primary = LEGACY_MODEL_MAP.get(primary_model, primary_model) or settings.PRIMARY_MODEL
    fallback = LEGACY_MODEL_MAP.get(fallback_model, fallback_model) or settings.FALLBACK_MODEL
    return primary, fallback
