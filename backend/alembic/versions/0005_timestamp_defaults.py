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


def _set_defaults(server_default) -> None:
    # SQLite cannot ALTER a column default, and tables there are already created
    # with the correct default, so this revision only needs to run on Postgres.
    if op.get_bind().dialect.name == "sqlite":
        return

    for table_name, columns in _TIMESTAMP_COLUMNS.items():
        for column_name in columns:
            op.alter_column(
                table_name,
                column_name,
                server_default=server_default,
                existing_type=sa.DateTime(timezone=True),
                existing_nullable=False,
            )


def upgrade() -> None:
    _set_defaults(sa.func.now())


def downgrade() -> None:
    _set_defaults(None)
