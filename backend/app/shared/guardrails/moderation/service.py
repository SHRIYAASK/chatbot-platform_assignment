import logging
import time

from app.shared.guardrails.input_guard import InputGuard
from app.shared.guardrails.moderation.categories import get_blocked_user_message
from app.shared.guardrails.moderation.classifier import RuleBasedClassifier
from app.shared.guardrails.moderation.constants import BLOCKED_USER_MESSAGE
from app.shared.guardrails.moderation.interfaces import ModerationProvider, ModerationResult
from app.shared.guardrails.moderation.logging_service import ModerationLoggingService
from app.shared.guardrails.moderation.policy import PolicyEngine
from app.shared.guardrails.output_guard import OutputGuard

logger = logging.getLogger(__name__)


class ModerationService:
    """Facade for input moderation. Chat module calls check() only."""

    _provider: ModerationProvider | None = None

    @classmethod
    def set_provider(cls, provider: ModerationProvider) -> None:
        cls._provider = provider

    @classmethod
    def get_provider(cls) -> ModerationProvider:
        if cls._provider is None:
            cls._provider = RuleBasedClassifier()
        return cls._provider

    @classmethod
    def check(
        cls,
        message: str,
        *,
        user_id: int | None = None,
        project_id: int | None = None,
    ) -> ModerationResult:
        start = time.perf_counter()
        provider = cls.get_provider()

        validated = InputGuard.validate(message)
        classification = provider.classify(validated)
        decision = provider.decide(classification)
        allowed = PolicyEngine.is_allowed(decision)

        latency_ms = int((time.perf_counter() - start) * 1000)
        result = ModerationResult(
            allowed=allowed,
            category=classification.category.value,
            subcategory=classification.subcategory,
            risk=classification.risk.value,
            decision=decision.value,
            reason=classification.reason,
            latency_ms=latency_ms,
        )

        if user_id is not None and project_id is not None:
            ModerationLoggingService.log_event(
                user_id=user_id,
                project_id=project_id,
                category=result.category,
                subcategory=result.subcategory,
                risk_level=result.risk,
                decision=result.decision,
                reason=result.reason,
                latency_ms=latency_ms,
            )

        logger.info(
            "Moderation decision=%s category=%s risk=%s latency_ms=%s",
            result.decision,
            result.category,
            result.risk,
            latency_ms,
        )
        return result

    @staticmethod
    def blocked_response_message() -> str:
        return get_blocked_user_message() or BLOCKED_USER_MESSAGE

    @staticmethod
    def sanitize_output(content: str) -> str:
        return OutputGuard.sanitize(content)
