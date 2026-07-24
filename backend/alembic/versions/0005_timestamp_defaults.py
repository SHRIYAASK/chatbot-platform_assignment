"""Restore timestamp defaults on legacy tables."""

from alembic import op
import sqlalchemy as sa

revision = "0005_timestamp_defaults"
down_revision = "0004_moderation_events"
branch_labels = None
depends_on = None

_TIMESTAMP_COLUMNS = {
    "users": ["created_at"],
    "projects": ["created_at", "updated_at"],
    "prompts": ["created_at", "updated_at"],
    "project_files": ["created_at"],
}


def upgrade() -> None:
    for table_name, columns in _TIMESTAMP_COLUMNS.items():
        for column_name in columns:
            op.alter_column(
                table_name,
                column_name,
                server_default=sa.text("now()"),
                existing_type=sa.DateTime(timezone=True),
                existing_nullable=False,
            )


def downgrade() -> None:
    for table_name, columns in _TIMESTAMP_COLUMNS.items():
        for column_name in columns:
            op.alter_column(
                table_name,
                column_name,
                server_default=None,
                existing_type=sa.DateTime(timezone=True),
                existing_nullable=False,
            )
