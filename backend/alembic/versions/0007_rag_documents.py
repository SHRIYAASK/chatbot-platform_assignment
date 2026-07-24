"""Add RAG document tables with optional pgvector support."""

from alembic import op
import sqlalchemy as sa

revision = "0007_rag_documents"
down_revision = "0006_drop_legacy_tables"
branch_labels = None
depends_on = None


def _pgvector_available(bind) -> bool:
    if bind.dialect.name != "postgresql":
        return False
    return bool(
        bind.execute(
            sa.text("SELECT EXISTS (SELECT 1 FROM pg_available_extensions WHERE name = 'vector')")
        ).scalar()
    )


def upgrade() -> None:
    bind = op.get_bind()
    use_pgvector = _pgvector_available(bind)
    if use_pgvector:
        op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "documents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("storage_key", sa.String(length=500), nullable=False),
        sa.Column("mime_type", sa.String(length=100), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="processing"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_documents_id"), "documents", ["id"], unique=False)
    op.create_index(op.f("ix_documents_project_id"), "documents", ["project_id"], unique=False)
    op.create_index(op.f("ix_documents_status"), "documents", ["status"], unique=False)

    op.create_table(
        "document_chunks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("document_id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("chunk_type", sa.String(length=10), nullable=False),
        sa.Column("parent_chunk_id", sa.Integer(), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("token_count", sa.Integer(), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["parent_chunk_id"], ["document_chunks.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    if use_pgvector:
        op.execute("ALTER TABLE document_chunks ADD COLUMN embedding vector(384)")
    else:
        op.add_column("document_chunks", sa.Column("embedding", sa.JSON(), nullable=True))

    op.create_index(op.f("ix_document_chunks_id"), "document_chunks", ["id"], unique=False)
    op.create_index(
        op.f("ix_document_chunks_document_id"),
        "document_chunks",
        ["document_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_document_chunks_project_id"),
        "document_chunks",
        ["project_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_document_chunks_chunk_type"),
        "document_chunks",
        ["chunk_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_document_chunks_parent_chunk_id"),
        "document_chunks",
        ["parent_chunk_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_document_chunks_parent_chunk_id"), table_name="document_chunks")
    op.drop_index(op.f("ix_document_chunks_chunk_type"), table_name="document_chunks")
    op.drop_index(op.f("ix_document_chunks_project_id"), table_name="document_chunks")
    op.drop_index(op.f("ix_document_chunks_document_id"), table_name="document_chunks")
    op.drop_index(op.f("ix_document_chunks_id"), table_name="document_chunks")
    op.drop_table("document_chunks")

    op.drop_index(op.f("ix_documents_status"), table_name="documents")
    op.drop_index(op.f("ix_documents_project_id"), table_name="documents")
    op.drop_index(op.f("ix_documents_id"), table_name="documents")
    op.drop_table("documents")
