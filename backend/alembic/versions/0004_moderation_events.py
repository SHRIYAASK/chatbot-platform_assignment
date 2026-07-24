"""Add moderation_events audit table."""

from alembic import op
import sqlalchemy as sa

revision = "0004_moderation_events"
down_revision = "0003_fix_legacy_models"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "moderation_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("subcategory", sa.String(length=50), nullable=True),
        sa.Column("risk_level", sa.String(length=20), nullable=False),
        sa.Column("decision", sa.String(length=20), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_moderation_events_id"), "moderation_events", ["id"], unique=False)
    op.create_index(
        op.f("ix_moderation_events_user_id"), "moderation_events", ["user_id"], unique=False
    )
    op.create_index(
        op.f("ix_moderation_events_project_id"),
        "moderation_events",
        ["project_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_moderation_events_project_id"), table_name="moderation_events")
    op.drop_index(op.f("ix_moderation_events_user_id"), table_name="moderation_events")
    op.drop_index(op.f("ix_moderation_events_id"), table_name="moderation_events")
    op.drop_table("moderation_events")
