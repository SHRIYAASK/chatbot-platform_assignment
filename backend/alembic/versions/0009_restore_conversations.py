"""Restore the conversations table and link chat messages to it.

Revision 0006 dropped the legacy ``conversations`` table and 0008 was committed
as an empty placeholder, so any database built purely from migrations (every
fresh deployment) never received the ``conversations`` table or the
``chat_messages.conversation_id`` column that the ORM models require. This
revision rebuilds both and is safe to run against databases that already have
them.
"""

from alembic import op
import sqlalchemy as sa

revision = "0009_restore_conversations"
down_revision = "0008_conversations"
branch_labels = None
depends_on = None

DEFAULT_CONVERSATION_TITLE = "General Chat"


def _table_names() -> set[str]:
    return set(sa.inspect(op.get_bind()).get_table_names())


def _column_names(table: str) -> set[str]:
    return {column["name"] for column in sa.inspect(op.get_bind()).get_columns(table)}


def _index_names(table: str) -> set[str]:
    return {index["name"] for index in sa.inspect(op.get_bind()).get_indexes(table)}


def _create_conversations_table() -> None:
    op.create_table(
        "conversations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column(
            "title",
            sa.String(length=200),
            nullable=False,
            server_default=DEFAULT_CONVERSATION_TITLE,
        ),
        sa.Column("is_pinned", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_conversations_id"), "conversations", ["id"], unique=False)
    op.create_index(
        op.f("ix_conversations_project_id"),
        "conversations",
        ["project_id"],
        unique=False,
    )


def _backfill_conversation_ids() -> None:
    """Give every pre-existing chat message a conversation to belong to."""
    bind = op.get_bind()
    project_ids = [
        row[0]
        for row in bind.execute(
            sa.text(
                "SELECT DISTINCT project_id FROM chat_messages "
                "WHERE conversation_id IS NULL"
            )
        )
    ]

    select_conversation = sa.text(
        "SELECT id FROM conversations WHERE project_id = :project_id "
        "ORDER BY id LIMIT 1"
    )

    for project_id in project_ids:
        conversation_id = bind.execute(
            select_conversation, {"project_id": project_id}
        ).scalar()

        if conversation_id is None:
            bind.execute(
                sa.text(
                    "INSERT INTO conversations (project_id, title) "
                    "VALUES (:project_id, :title)"
                ),
                {"project_id": project_id, "title": DEFAULT_CONVERSATION_TITLE},
            )
            conversation_id = bind.execute(
                select_conversation, {"project_id": project_id}
            ).scalar()

        bind.execute(
            sa.text(
                "UPDATE chat_messages SET conversation_id = :conversation_id "
                "WHERE project_id = :project_id AND conversation_id IS NULL"
            ),
            {"conversation_id": conversation_id, "project_id": project_id},
        )


def upgrade() -> None:
    if "conversations" not in _table_names():
        _create_conversations_table()

    if "conversation_id" in _column_names("chat_messages"):
        return

    op.add_column("chat_messages", sa.Column("conversation_id", sa.Integer(), nullable=True))
    _backfill_conversation_ids()

    # batch_alter_table keeps this migration runnable on SQLite, which cannot
    # ALTER an existing column or add a foreign key in place.
    with op.batch_alter_table("chat_messages") as batch_op:
        batch_op.alter_column(
            "conversation_id",
            existing_type=sa.Integer(),
            nullable=False,
        )
        batch_op.create_foreign_key(
            "fk_chat_messages_conversation_id_conversations",
            "conversations",
            ["conversation_id"],
            ["id"],
            ondelete="CASCADE",
        )

    if "ix_chat_messages_conversation_id" not in _index_names("chat_messages"):
        op.create_index(
            op.f("ix_chat_messages_conversation_id"),
            "chat_messages",
            ["conversation_id"],
            unique=False,
        )


def downgrade() -> None:
    if "conversation_id" in _column_names("chat_messages"):
        if "ix_chat_messages_conversation_id" in _index_names("chat_messages"):
            op.drop_index(
                op.f("ix_chat_messages_conversation_id"),
                table_name="chat_messages",
            )
        with op.batch_alter_table("chat_messages") as batch_op:
            batch_op.drop_constraint(
                "fk_chat_messages_conversation_id_conversations",
                type_="foreignkey",
            )
            batch_op.drop_column("conversation_id")

    if "conversations" in _table_names():
        op.drop_index(op.f("ix_conversations_project_id"), table_name="conversations")
        op.drop_index(op.f("ix_conversations_id"), table_name="conversations")
        op.drop_table("conversations")
