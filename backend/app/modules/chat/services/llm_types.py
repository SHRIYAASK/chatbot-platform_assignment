from dataclasses import dataclass


@dataclass(frozen=True)
class LLMResult:
    content: str
    model_used: str
    token_count: int | None = None
