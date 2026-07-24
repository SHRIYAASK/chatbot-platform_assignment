"""Backward-compatible re-export.

The canonical implementation now lives in ``app.shared.authorization``.
"""

from app.shared.authorization.project_access import get_owned_project_or_403

__all__ = ["get_owned_project_or_403"]
