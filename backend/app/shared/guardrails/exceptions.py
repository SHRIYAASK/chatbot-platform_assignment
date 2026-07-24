"""Guardrail and moderation exceptions."""

from app.shared.guardrails.moderation.constants import ModerationDecision


class GuardrailError(Exception):
    """Base guardrail exception."""


class InputValidationError(GuardrailError):
    """Raised when user input fails structural validation."""


class ModerationBlockedError(GuardrailError):
    """Raised when moderation policy blocks a request."""

    def __init__(
        self,
        category: str,
        risk: str,
        decision: ModerationDecision,
        user_message: str,
        reason: str | None = None,
    ):
        self.category = category
        self.risk = risk
        self.decision = decision
        self.user_message = user_message
        self.reason = reason
        super().__init__(user_message)
