"""Add failure_reason to documents for clearer RAG indexing errors."""

from alembic import op
import sqlalchemy as sa

revision = "0010_document_failure_reason"
down_revision = "0009_restore_conversations"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    columns = {column["name"] for column in sa.inspect(bind).get_columns("documents")}
    if "failure_reason" not in columns:
        op.add_column("documents", sa.Column("failure_reason", sa.String(length=500), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    columns = {column["name"] for column in sa.inspect(bind).get_columns("documents")}
    if "failure_reason" in columns:
        op.drop_column("documents", "failure_reason")
