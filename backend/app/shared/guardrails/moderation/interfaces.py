from dataclasses import dataclass
from typing import Protocol

from app.shared.guardrails.moderation.constants import (
    ModerationCategory,
    ModerationDecision,
    RiskLevel,
)


@dataclass(frozen=True)
class ClassificationResult:
    category: ModerationCategory
    subcategory: str | None
    risk: RiskLevel
    reason: str | None = None
    matched_pattern: str | None = None


@dataclass(frozen=True)
class ModerationResult:
    allowed: bool
    category: str
    subcategory: str | None
    risk: str
    decision: str
    reason: str | None = None
    latency_ms: int = 0

    def to_dict(self) -> dict:
        return {
            "allowed": self.allowed,
            "category": self.category,
            "subcategory": self.subcategory,
            "risk": self.risk,
            "decision": self.decision,
            "reason": self.reason,
            "latency_ms": self.latency_ms,
        }


class ModerationProvider(Protocol):
    """Interface for pluggable moderation backends (local rules, OpenAI, Azure, etc.)."""

    def classify(self, message: str) -> ClassificationResult: ...

    def decide(self, classification: ClassificationResult) -> ModerationDecision: ...
