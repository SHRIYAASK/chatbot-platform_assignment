"""Placeholder revision — keeps Alembic history consistent with the database."""

from alembic import op

revision = "0008_conversations"
down_revision = "0007_rag_documents"
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
