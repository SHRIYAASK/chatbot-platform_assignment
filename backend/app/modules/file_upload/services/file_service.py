import os
import uuid
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.modules.authentication.models.user import User
from app.modules.file_upload.models.file import ProjectFile
from app.shared.authorization.project_access import get_owned_project_or_403

MAX_FILE_SIZE = 10 * 1024 * 1024
READ_CHUNK_SIZE = 1024 * 1024

ALLOWED_EXTENSIONS = {".txt", ".pdf", ".md", ".json"}
ALLOWED_CONTENT_TYPES = {
    "text/plain",
    "application/pdf",
    "text/markdown",
    "application/json",
}

FILE_SIGNATURES: dict[str, tuple[bytes, ...]] = {
    ".pdf": (b"%PDF-",),
    ".json": (b"{", b"["),
}


class FileService:
    @staticmethod
    def _upload_dir() -> Path:
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)
        return upload_dir

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

        if extension in {".txt", ".md"}:
            try:
                sample.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise ValueError("Text file must be valid UTF-8.") from exc

        return extension

    @staticmethod
    async def _read_with_limit(upload: UploadFile) -> bytes:
        chunks: list[bytes] = []
        total_size = 0

        while True:
            chunk = await upload.read(READ_CHUNK_SIZE)
            if not chunk:
                break
            total_size += len(chunk)
            if total_size > MAX_FILE_SIZE:
                raise ValueError("File exceeds maximum size of 10MB.")
            chunks.append(chunk)

        return b"".join(chunks)

    @staticmethod
    def list_files(db: Session, current_user: User, project_id: int) -> list[ProjectFile]:
        get_owned_project_or_403(db, project_id, current_user)
        return (
            db.query(ProjectFile)
            .filter(ProjectFile.project_id == project_id)
            .order_by(ProjectFile.created_at.desc())
            .all()
        )

    @staticmethod
    async def upload_file(
        db: Session,
        current_user: User,
        project_id: int,
        upload: UploadFile,
    ) -> ProjectFile:
        get_owned_project_or_403(db, project_id, current_user)

        content = await FileService._read_with_limit(upload)
        extension = FileService._validate_file_type(
            upload.filename or "file.txt",
            upload.content_type,
            content[:512],
        )

        stored_name = f"{uuid.uuid4().hex}{extension}"
        stored_path = FileService._upload_dir() / stored_name

        with open(stored_path, "wb") as file_handle:
            file_handle.write(content)

        project_file = ProjectFile(
            project_id=project_id,
            filename=upload.filename or stored_name,
            file_path=str(stored_path),
            file_size=len(content),
            content_type=upload.content_type or "application/octet-stream",
        )
        db.add(project_file)
        db.commit()
        db.refresh(project_file)
        return project_file

    @staticmethod
    def delete_file(
        db: Session,
        current_user: User,
        project_id: int,
        file_id: int,
    ) -> None:
        get_owned_project_or_403(db, project_id, current_user)
        project_file = (
            db.query(ProjectFile)
            .filter(ProjectFile.id == file_id, ProjectFile.project_id == project_id)
            .first()
        )
        if project_file is None:
            raise ValueError("File not found.")

        if os.path.exists(project_file.file_path):
            os.remove(project_file.file_path)

        db.delete(project_file)
        db.commit()
