"""Add composite index for chat history queries."""

from alembic import op

revision = "0002_chat_history_index"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "ix_chat_messages_project_id_created_at",
        "chat_messages",
        ["project_id", "created_at"],
        unique=False,
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_index("ix_chat_messages_project_id_created_at", table_name="chat_messages")
