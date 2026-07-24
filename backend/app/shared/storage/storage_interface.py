from abc import ABC, abstractmethod


class StorageInterface(ABC):
    """Abstract storage provider. Swap implementations without changing business logic."""

    @abstractmethod
    async def upload(self, key: str, data: bytes, content_type: str) -> str:
        """Persist bytes at the given key and return the storage key."""

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Remove the object at the given key if it exists."""

    @abstractmethod
    async def download(self, key: str) -> bytes:
        """Return the raw bytes for the given key."""

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Return True when the object exists."""

    @abstractmethod
    def generate_url(self, key: str, expires_in: int = 3600) -> str | None:
        """Return a temporary access URL when supported by the provider."""
