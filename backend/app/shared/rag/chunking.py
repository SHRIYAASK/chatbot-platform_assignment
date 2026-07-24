import re
from dataclasses import dataclass
from pathlib import Path

from app.shared.config.rag_settings import (
    CHILD_CHUNK_MAX_TOKENS,
    CHILD_CHUNK_TARGET_TOKENS,
    PARENT_CHUNK_MAX_TOKENS,
    PARENT_CHUNK_TARGET_TOKENS,
)


def estimate_tokens(text: str) -> int:
    """Approximate token count without an external tokenizer."""
    stripped = text.strip()
    if not stripped:
        return 0
    return max(1, len(stripped) // 4)


def _split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+|\n{2,}", text.strip())
    return [part.strip() for part in parts if part.strip()]


def _pack_units(units: list[str], target_tokens: int, max_tokens: int) -> list[str]:
    chunks: list[str] = []
    current: list[str] = []
    current_tokens = 0

    for unit in units:
        unit_tokens = estimate_tokens(unit)
        if unit_tokens > max_tokens:
            if current:
                chunks.append("\n\n".join(current))
                current = []
                current_tokens = 0
            chunks.append(unit)
            continue

        projected = current_tokens + unit_tokens
        if current and projected > max_tokens:
            chunks.append("\n\n".join(current))
            current = [unit]
            current_tokens = unit_tokens
            continue

        current.append(unit)
        current_tokens = projected
        if current_tokens >= target_tokens:
            chunks.append("\n\n".join(current))
            current = []
            current_tokens = 0

    if current:
        chunks.append("\n\n".join(current))

    return chunks


def _split_by_tokens(text: str, target_tokens: int, max_tokens: int) -> list[str]:
    words = text.split()
    if not words:
        return []

    chunks: list[str] = []
    current: list[str] = []
    current_tokens = 0

    for word in words:
        word_tokens = estimate_tokens(word)
        projected = current_tokens + word_tokens
        if current and projected > max_tokens:
            chunks.append(" ".join(current))
            current = [word]
            current_tokens = word_tokens
            continue

        current.append(word)
        current_tokens = projected
        if current_tokens >= target_tokens:
            chunks.append(" ".join(current))
            current = []
            current_tokens = 0

    if current:
        chunks.append(" ".join(current))

    return chunks


@dataclass(frozen=True)
class ParentChunk:
    content: str
    token_count: int
    chunk_index: int


@dataclass(frozen=True)
class ChildChunk:
    content: str
    token_count: int
    chunk_index: int
    parent_index: int


@dataclass(frozen=True)
class ChunkingResult:
    parents: list[ParentChunk]
    children: list[ChildChunk]


def chunk_document(text: str) -> ChunkingResult:
    """Split document text into parent and child chunks for RAG indexing."""
    normalized = text.strip()
    if not normalized:
        return ChunkingResult(parents=[], children=[])

    sentences = _split_sentences(normalized)
    parent_texts = _pack_units(
        sentences,
        target_tokens=PARENT_CHUNK_TARGET_TOKENS,
        max_tokens=PARENT_CHUNK_MAX_TOKENS,
    )

    parents: list[ParentChunk] = []
    children: list[ChildChunk] = []

    for parent_index, parent_text in enumerate(parent_texts):
        token_count = estimate_tokens(parent_text)
        parents.append(
            ParentChunk(
                content=parent_text,
                token_count=token_count,
                chunk_index=parent_index,
            )
        )

        child_texts = _split_by_tokens(
            parent_text,
            target_tokens=CHILD_CHUNK_TARGET_TOKENS,
            max_tokens=CHILD_CHUNK_MAX_TOKENS,
        )
        for child_index, child_text in enumerate(child_texts):
            children.append(
                ChildChunk(
                    content=child_text,
                    token_count=estimate_tokens(child_text),
                    chunk_index=child_index,
                    parent_index=parent_index,
                )
            )

    return ChunkingResult(parents=parents, children=children)
