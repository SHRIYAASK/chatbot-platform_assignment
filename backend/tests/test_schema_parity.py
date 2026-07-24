"""Guard against drift between Alembic migrations and the ORM models.

The test database is built by running the migration chain (see conftest), so
comparing it to ``Base.metadata`` catches the class of bug where a model exists
but no migration ever creates its table or column.
"""

from sqlalchemy import inspect

from app.core.database import Base, engine

# Alembic bookkeeping is not part of the ORM metadata.
IGNORED_TABLES = {"alembic_version"}


def _migrated_tables() -> set[str]:
    return set(inspect(engine).get_table_names()) - IGNORED_TABLES


def test_every_model_table_exists_in_migrations():
    missing = set(Base.metadata.tables) - _migrated_tables()
    assert not missing, f"Models without a migration-created table: {sorted(missing)}"


def test_no_orphaned_tables_left_by_migrations():
    orphaned = _migrated_tables() - set(Base.metadata.tables)
    assert not orphaned, f"Tables created by migrations but not modelled: {sorted(orphaned)}"


def test_every_model_column_exists_in_migrations():
    inspector = inspect(engine)
    mismatches: list[str] = []

    for table_name, table in Base.metadata.tables.items():
        migrated_columns = {column["name"] for column in inspector.get_columns(table_name)}
        for column in table.columns:
            if column.name not in migrated_columns:
                mismatches.append(f"{table_name}.{column.name}")

    assert not mismatches, f"Model columns missing from migrations: {sorted(mismatches)}"


def test_conversations_are_linked_to_chat_messages():
    """Regression test for the migration that dropped conversations and never restored it."""
    inspector = inspect(engine)

    assert "conversations" in _migrated_tables()

    chat_message_columns = {column["name"] for column in inspector.get_columns("chat_messages")}
    assert "conversation_id" in chat_message_columns

    referenced = {
        fk["referred_table"] for fk in inspector.get_foreign_keys("chat_messages")
    }
    assert "conversations" in referenced
