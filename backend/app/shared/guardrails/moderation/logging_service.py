import logging

from app.core.database import SessionLocal
from app.shared.guardrails.moderation.models import ModerationEvent


logger = logging.getLogger(__name__)


class ModerationLoggingService:
    @staticmethod
    def log_event(
        *,
        user_id: int,
        project_id: int,
        category: str,
        subcategory: str | None,
        risk_level: str,
        decision: str,
        reason: str | None,
        latency_ms: int,
    ) -> None:
        db = SessionLocal()
        try:
            event = ModerationEvent(
                user_id=user_id,
                project_id=project_id,
                category=category,
                subcategory=subcategory,
                risk_level=risk_level,
                decision=decision,
                reason=reason,
                latency_ms=latency_ms,
            )
            db.add(event)
            db.commit()
        except Exception:
            db.rollback()
            logger.exception("Failed to persist moderation event")
        finally:
            db.close()
