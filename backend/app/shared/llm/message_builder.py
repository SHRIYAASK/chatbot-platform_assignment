"""Provider-agnostic chat message assembly for LLM requests."""

from app.shared.llm.system_prompt_builder import build_system_prompt


def build_chat_messages(
    project_description: str,
    history: list[dict[str, str]],
    user_message: str,
    rag_context: str | None = None,
) -> list[dict[str, str]]:
    """Build provider-agnostic messages in chronological order.

    Message order:
    1. System prompt (guardrails + project instructions + response style)
    2. Optional RAG context as a separate system message
    3. Previous conversation history
    4. Current user message

    Conversation history is never embedded inside the system prompt.
    """
    messages: list[dict[str, str]] = [
        {"role": "system", "content": build_system_prompt(project_description)},
    ]

    if rag_context:
        messages.append({"role": "system", "content": rag_context.strip()})

    for entry in history:
        role = entry.get("role", "").strip()
        content = entry.get("content", "").strip()
        if role in {"user", "assistant"} and content:
            messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": user_message.strip()})
    return messages
