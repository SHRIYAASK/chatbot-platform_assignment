from app.shared.guardrails.moderation.categories import get_categories_config, get_decision_matrix
from app.shared.guardrails.moderation.constants import ModerationDecision
from app.shared.guardrails.moderation.interfaces import ClassificationResult


class PolicyEngine:
    """Maps classification results to moderation decisions."""

    def __init__(self):
        self._matrix = get_decision_matrix()

    def decide(self, classification: ClassificationResult) -> ModerationDecision:
        categories = get_categories_config()
        category_config = categories.get(classification.category.value, {})

        if classification.subcategory:
            sub_config = category_config.get("subcategories", {}).get(
                classification.subcategory, {}
            )
            sub_decision = sub_config.get("decision")
            if sub_decision:
                return ModerationDecision(sub_decision)

        category_decision = category_config.get("default_decision")
        if category_decision:
            return ModerationDecision(category_decision)

        matrix_decision = self._matrix.get(classification.risk.value, "ALLOW")
        return ModerationDecision(matrix_decision)

    @staticmethod
    def is_allowed(decision: ModerationDecision) -> bool:
        return decision != ModerationDecision.BLOCK
