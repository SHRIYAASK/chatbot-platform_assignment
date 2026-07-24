"""Fix legacy model names stored on projects."""

from alembic import op

revision = "0003_fix_legacy_models"
down_revision = "0002_chat_history_index"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE projects
        SET primary_model = 'openai/gpt-oss-120b'
        WHERE primary_model = 'grok-opus-4-120b'
        """
    )
    op.execute(
        """
        UPDATE projects
        SET fallback_model = 'llama-3.3-70b-versatile'
        WHERE fallback_model = 'llama-3.3-70b'
        """
    )


def downgrade() -> None:
    op.execute(
        """
        UPDATE projects
        SET primary_model = 'grok-opus-4-120b'
        WHERE primary_model = 'openai/gpt-oss-120b'
        """
    )
    op.execute(
        """
        UPDATE projects
        SET fallback_model = 'llama-3.3-70b'
        WHERE fallback_model = 'llama-3.3-70b-versatile'
        """
    )
