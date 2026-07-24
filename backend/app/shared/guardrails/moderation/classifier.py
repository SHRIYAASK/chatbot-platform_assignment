from app.shared.guardrails.moderation.constants import (
    ModerationCategory,
    ModerationDecision,
    RiskLevel,
)
from app.shared.guardrails.moderation.interfaces import ClassificationResult
from app.shared.guardrails.moderation.policy import PolicyEngine
from app.shared.guardrails.moderation.rules import CategoryRule, build_category_rules


class RuleBasedClassifier:
    """Local rule-based classifier. Swap for external providers via ModerationProvider."""

    def __init__(self, rules: list[CategoryRule] | None = None):
        self._rules = rules if rules is not None else build_category_rules()
        self._policy = PolicyEngine()

    def classify(self, message: str) -> ClassificationResult:
        normalized = message.lower().strip()

        for rule in self._rules:
            if rule.pattern.search(normalized):
                return ClassificationResult(
                    category=ModerationCategory(rule.category),
                    subcategory=rule.subcategory,
                    risk=RiskLevel(rule.risk),
                    reason=f"Matched {rule.category} rule",
                    matched_pattern=rule.pattern.pattern,
                )

        return ClassificationResult(
            category=ModerationCategory.SAFE,
            subcategory=None,
            risk=RiskLevel.LOW,
            reason="No policy rule matched",
        )

    def decide(self, classification: ClassificationResult) -> ModerationDecision:
        return self._policy.decide(classification)
