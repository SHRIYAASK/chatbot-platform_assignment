"""Build the final system prompt from independent platform and project layers."""

from app.shared.llm.platform_guardrails import PLATFORM_SYSTEM_PROMPT
from app.shared.llm.response_style import GLOBAL_RESPONSE_STYLE

DEFAULT_PROJECT_INSTRUCTIONS = "You are a helpful AI assistant."

_LAYER_SEPARATOR = "\n\n---\n\n"


def normalize_project_instructions(project_description: str) -> str:
    """Return trimmed project instructions or the platform default."""
    instructions = project_description.strip()
    return instructions or DEFAULT_PROJECT_INSTRUCTIONS


def build_system_prompt(project_description: str) -> str:
    """Combine platform rules, project instructions, and response style.

    Layer order is fixed and must not change:
    1. Platform System Prompt
    2. Project Instructions (project description)
    3. Global Response Style
    """
    project_instructions = normalize_project_instructions(project_description)

    return _LAYER_SEPARATOR.join(
        [
            PLATFORM_SYSTEM_PROMPT,
            f"PROJECT INSTRUCTIONS\n\n{project_instructions}",
            GLOBAL_RESPONSE_STYLE,
        ]
    )
