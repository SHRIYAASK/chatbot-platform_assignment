from app.shared.config.rag_settings import MAX_CONTEXT_CHARS
from app.shared.rag.retriever import RetrievedContext


def build_rag_system_message(contexts: list[RetrievedContext]) -> str | None:
    """Build a system prompt section from retrieved document context."""
    if not contexts:
        return None

    sections: list[str] = []
    total_chars = 0

    for index, context in enumerate(contexts, start=1):
        section = (
            f"[Document excerpt {index} | relevance={context.score:.2f}]\n"
            f"{context.parent_content.strip()}"
        )
        if total_chars + len(section) > MAX_CONTEXT_CHARS:
            break
        sections.append(section)
        total_chars += len(section)

    if not sections:
        return None

    joined = "\n\n---\n\n".join(sections)
    return (
        "Use the following project document excerpts to answer the user's question. "
        "If the excerpts are not relevant, rely on your general knowledge and clearly "
        "state when project documents do not contain the answer.\n\n"
        f"{joined}"
    )
