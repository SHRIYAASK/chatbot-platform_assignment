from functools import lru_cache

from app.core.config import settings
from app.shared.storage.local_storage import LocalStorageProvider
from app.shared.storage.storage_interface import StorageInterface


class StorageFactory:
    """Select the active storage provider from configuration."""

    @staticmethod
    def create() -> StorageInterface:
        provider = settings.STORAGE_PROVIDER.strip().lower()
        if provider == "local":
            return LocalStorageProvider()
        raise ValueError(
            f"Unsupported storage provider: {provider}. "
            "Supported values: local."
        )


@lru_cache(maxsize=1)
def get_storage_service() -> StorageInterface:
    return StorageFactory.create()
