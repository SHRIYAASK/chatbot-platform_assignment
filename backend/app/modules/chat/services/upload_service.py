import logging
import uuid
from pathlib import Path

import httpx
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.modules.authentication.models.user import User
from app.modules.chat.models.document import Document
from app.modules.chat.models.document_chunk import DocumentChunk
from app.shared.authorization.project_access import get_owned_project_or_403
from app.shared.config.rag_settings import (
    ALLOWED_CONTENT_TYPES,
    ALLOWED_EXTENSIONS,
    FILE_SIGNATURES,
    MAX_FILE_SIZE_BYTES,
    READ_CHUNK_SIZE,
)
from app.shared.rag.chunking import chunk_document
from app.shared.rag.embedding_service import EmbeddingService, get_embedding_service
from app.shared.rag.text_extractor import TextExtractionError, extract_text
from app.shared.rag.vector_store import VectorStore
from app.shared.storage.storage_interface import StorageInterface

logger = logging.getLogger(__name__)


class UploadService:
    """Orchestrates document upload, storage, chunking, and embedding."""

    def __init__(
        self,
        storage: StorageInterface,
        embedding_service: EmbeddingService,
    ) -> None:
        self._storage = storage
        self._embedding_service = embedding_service

    @staticmethod
    def list_documents(
        db: Session,
        current_user: User,
        project_id: int,
    ) -> list[Document]:
        get_owned_project_or_403(db, project_id, current_user)
        return (
            db.query(Document)
            .filter(Document.project_id == project_id)
            .order_by(Document.created_at.desc())
            .all()
        )

    async def upload_document(
        self,
        db: Session,
        current_user: User,
        project_id: int,
        upload: UploadFile,
    ) -> tuple[Document, bytes]:
        """Validate, store file, and create a processing document record."""
        get_owned_project_or_403(db, project_id, current_user)

        content = await self._read_with_limit(upload)
        extension = self._validate_file_type(
            upload.filename or "file.txt",
            upload.content_type,
            content[:512],
        )

        original_name = upload.filename or f"document{extension}"
        storage_key = self._build_storage_key(project_id, original_name, extension)
        mime_type = upload.content_type or "application/octet-stream"

        await self._storage.upload(storage_key, content, mime_type)

        document = Document(
            project_id=project_id,
            filename=original_name,
            storage_key=storage_key,
            mime_type=mime_type,
            file_size=len(content),
            status="processing",
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        return document, content

    @staticmethod
    def index_document(document_id: int, content: bytes) -> None:
        """Index document content in a background worker thread."""
        db = SessionLocal()
        document = db.query(Document).filter(Document.id == document_id).first()
        if document is None:
            db.close()
            return

        embedding_service = get_embedding_service()

        try:
            chunks_indexed = UploadService._index_document(
                db,
                document,
                content,
                embedding_service,
            )
            document.status = "ready"
            db.commit()
            logger.info(
                "Indexed document %s (%s chunks)",
                document_id,
                chunks_indexed,
            )
        except (TextExtractionError, ValueError) as exc:
            db.rollback()
            UploadService._mark_document_failed(db, document_id, str(exc))
            logger.warning("Document %s indexing failed: %s", document_id, exc)
        except httpx.HTTPStatusError as exc:
            db.rollback()
            reason = UploadService._embedding_http_error_message(exc)
            UploadService._mark_document_failed(db, document_id, reason)
            logger.warning("Document %s embedding failed: %s", document_id, reason)
        except Exception as exc:
            db.rollback()
            reason = UploadService._unexpected_indexing_error_message(exc)
            UploadService._mark_document_failed(db, document_id, reason)
            logger.exception("Document %s indexing failed unexpectedly", document_id)
        finally:
            db.close()

    @staticmethod
    def _embedding_http_error_message(exc: httpx.HTTPStatusError) -> str:
        if exc.response.status_code in {401, 403}:
            return (
                "Embedding API authentication failed. Set a valid EMBEDDING_API_KEY "
                "on the backend server."
            )
        if exc.response.status_code == 429:
            return "Embedding API rate limit exceeded. Try again in a few minutes."
        return f"Embedding API request failed with status {exc.response.status_code}."

    @staticmethod
    def _unexpected_indexing_error_message(exc: Exception) -> str:
        message = str(exc).strip()
        if "Hugging Face embedding request failed" in message:
            return (
                "Embedding service is unavailable. Verify EMBEDDING_API_KEY and "
                "EMBEDDING_PROVIDER on the backend server."
            )
        return message or "Unexpected indexing error."

    @staticmethod
    def _mark_document_failed(db: Session, document_id: int, reason: str) -> None:
        document = db.query(Document).filter(Document.id == document_id).first()
        if document is None:
            return
        document.status = "failed"
        document.failure_reason = reason[:500]
        db.commit()

    async def delete_document(
        self,
        db: Session,
        current_user: User,
        project_id: int,
        document_id: int,
    ) -> None:
        get_owned_project_or_403(db, project_id, current_user)
        document = (
            db.query(Document)
            .filter(Document.id == document_id, Document.project_id == project_id)
            .first()
        )
        if document is None:
            raise ValueError("Document not found.")

        await self._storage.delete(document.storage_key)
        db.delete(document)
        db.commit()

    @staticmethod
    def _index_document(
        db: Session,
        document: Document,
        content: bytes,
        embedding_service: EmbeddingService,
    ) -> int:
        text = extract_text(document.filename, content)
        chunking_result = chunk_document(text)
        if not chunking_result.children:
            raise ValueError("Document did not produce searchable content.")

        parent_models: list[DocumentChunk] = []
        for parent in chunking_result.parents:
            parent_chunk = DocumentChunk(
                document_id=document.id,
                project_id=document.project_id,
                chunk_type="parent",
                parent_chunk_id=None,
                content=parent.content,
                token_count=parent.token_count,
                chunk_index=parent.chunk_index,
                embedding=None,
            )
            db.add(parent_chunk)
            parent_models.append(parent_chunk)

        db.flush()

        child_models: list[DocumentChunk] = []
        child_texts: list[str] = []
        for child in chunking_result.children:
            parent_model = parent_models[child.parent_index]
            child_chunk = DocumentChunk(
                document_id=document.id,
                project_id=document.project_id,
                chunk_type="child",
                parent_chunk_id=parent_model.id,
                content=child.content,
                token_count=child.token_count,
                chunk_index=child.chunk_index,
                embedding=None,
            )
            db.add(child_chunk)
            child_models.append(child_chunk)
            child_texts.append(child.content)

        db.flush()

        embeddings = embedding_service.embed_texts(child_texts)
        vector_store = VectorStore(db, embedding_service)
        vector_store.store_child_embeddings(
            [chunk.id for chunk in child_models],
            embeddings,
        )
        db.flush()
        return len(child_models)

    @staticmethod
    def _build_storage_key(project_id: int, filename: str, extension: str) -> str:
        safe_name = Path(filename).name.replace(" ", "_")
        if not safe_name.lower().endswith(extension):
            safe_name = f"{Path(safe_name).stem}{extension}"
        unique_name = f"{uuid.uuid4().hex}_{safe_name}"
        return f"project_{project_id}/{unique_name}"

    @staticmethod
    async def _read_with_limit(upload: UploadFile) -> bytes:
        chunks: list[bytes] = []
        total_size = 0

        while True:
            chunk = await upload.read(READ_CHUNK_SIZE)
            if not chunk:
                break
            total_size += len(chunk)
            if total_size > MAX_FILE_SIZE_BYTES:
                raise ValueError("File exceeds maximum size of 10MB.")
            chunks.append(chunk)

        if total_size == 0:
            raise ValueError("Uploaded file is empty.")

        return b"".join(chunks)

    @staticmethod
    def _validate_file_type(filename: str, content_type: str | None, sample: bytes) -> str:
        extension = Path(filename or "file.txt").suffix.lower()
        if extension not in ALLOWED_EXTENSIONS:
            raise ValueError("Unsupported file extension.")

        if content_type and content_type not in ALLOWED_CONTENT_TYPES:
            raise ValueError("Unsupported file type.")

        signatures = FILE_SIGNATURES.get(extension)
        if signatures and not any(sample.startswith(signature) for signature in signatures):
            raise ValueError("File content does not match the declared type.")

        if extension in {".txt", ".md", ".json"}:
            try:
                sample.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise ValueError("Text file must be valid UTF-8.") from exc

        return extension
