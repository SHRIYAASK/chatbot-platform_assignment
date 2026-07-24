from pathlib import Path

import aiofiles

from app.core.config import settings
from app.shared.storage.storage_interface import StorageInterface


class LocalStorageProvider(StorageInterface):
    """Development storage provider that writes files under backend/uploads/."""

    def __init__(self, base_dir: str | None = None) -> None:
        self._base_dir = Path(base_dir or settings.UPLOAD_DIR)

    def _resolve_path(self, key: str) -> Path:
        normalized = key.replace("\\", "/").lstrip("/")
        path = (self._base_dir / normalized).resolve()
        base = self._base_dir.resolve()
        if base not in path.parents and path != base:
            raise ValueError("Invalid storage key.")
        return path

    async def upload(self, key: str, data: bytes, content_type: str) -> str:
        path = self._resolve_path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(path, "wb") as handle:
            await handle.write(data)
        return key

    async def delete(self, key: str) -> None:
        path = self._resolve_path(key)
        if path.exists():
            path.unlink()

    async def download(self, key: str) -> bytes:
        path = self._resolve_path(key)
        if not path.exists():
            raise FileNotFoundError(f"Storage object not found: {key}")
        async with aiofiles.open(path, "rb") as handle:
            return await handle.read()

    async def exists(self, key: str) -> bool:
        return self._resolve_path(key).exists()

    def generate_url(self, key: str, expires_in: int = 3600) -> str | None:
        return None
