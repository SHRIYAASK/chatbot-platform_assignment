import hashlib
import math
import time
from abc import ABC, abstractmethod
from functools import lru_cache

import httpx

from app.core.config import settings

API_KEY_PROVIDERS = {"huggingface", "hf", "http"}
BATCH_SIZE = 16
MAX_RETRIES = 3


class EmbeddingService(ABC):
    """Generate vector embeddings for retrieval."""

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Embedding vector size."""

    @abstractmethod
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of texts."""


class HashEmbeddingService(EmbeddingService):
    """Deterministic local embeddings for tests and offline development."""

    def __init__(self, dimension: int = 384) -> None:
        self._dimension = dimension

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_one(text) for text in texts]

    def _embed_one(self, text: str) -> list[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        values: list[float] = []
        seed = int.from_bytes(digest[:8], "big")

        while len(values) < self._dimension:
            seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
            values.append((seed / 0x7FFFFFFF) * 2 - 1)

        norm = math.sqrt(sum(value * value for value in values)) or 1.0
        return [value / norm for value in values]


class HuggingFaceEmbeddingService(EmbeddingService):
    """Hugging Face Inference API embeddings."""

    def __init__(
        self,
        api_key: str,
        model: str,
        dimension: int,
        api_url: str,
    ) -> None:
        self._api_key = api_key
        self._model = model.strip()
        self._dimension = dimension
        base = api_url.rstrip("/")
        if base.endswith(self._model):
            self._endpoint = base
        else:
            self._endpoint = f"{base}/{self._model}"

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        embeddings: list[list[float]] = []
        for start in range(0, len(texts), BATCH_SIZE):
            batch = texts[start : start + BATCH_SIZE]
            embeddings.extend(self._embed_batch(batch))
        return embeddings

    def _embed_batch(self, texts: list[str]) -> list[list[float]]:
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        payload = {"inputs": texts[0] if len(texts) == 1 else texts}

        last_error: Exception | None = None
        for attempt in range(MAX_RETRIES):
            try:
                response = httpx.post(
                    self._endpoint,
                    json=payload,
                    headers=headers,
                    timeout=120.0,
                )
                if response.status_code in {503, 504}:
                    time.sleep(2 ** attempt)
                    continue
                response.raise_for_status()
                return self._normalize_response(response.json(), len(texts))
            except Exception as exc:
                last_error = exc
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise

        raise RuntimeError("Hugging Face embedding request failed.") from last_error

    def _normalize_response(self, payload, expected_count: int) -> list[list[float]]:
        if expected_count == 1:
            return [self._normalize_vector(payload)]

        if not isinstance(payload, list) or len(payload) != expected_count:
            raise ValueError("Unexpected Hugging Face embedding response shape.")

        return [self._normalize_vector(item) for item in payload]

    def _normalize_vector(self, payload) -> list[float]:
        if isinstance(payload, list) and payload and isinstance(payload[0], (int, float)):
            return [float(value) for value in payload]

        if isinstance(payload, list) and payload and isinstance(payload[0], list):
            token_vectors = payload
            if not token_vectors:
                raise ValueError("Empty token vectors returned by Hugging Face.")
            length = len(token_vectors[0])
            pooled = [0.0] * length
            for vector in token_vectors:
                for index, value in enumerate(vector):
                    pooled[index] += float(value)
            return [value / len(token_vectors) for value in pooled]

        raise ValueError("Unable to parse Hugging Face embedding response.")


class FastEmbedEmbeddingService(EmbeddingService):
    """Local embedding model via fastembed."""

    def __init__(self, model_name: str) -> None:
        from fastembed import TextEmbedding

        self._model = TextEmbedding(model_name=model_name)
        sample = next(self._model.embed(["dimension probe"]))
        self._dimension = len(list(sample))

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [list(vector) for vector in self._model.embed(texts)]


class HttpEmbeddingService(EmbeddingService):
    """OpenAI-compatible HTTP embedding provider."""

    def __init__(
        self,
        api_url: str,
        api_key: str,
        model: str,
        dimension: int,
    ) -> None:
        self._api_url = api_url.rstrip("/")
        self._api_key = api_key
        self._model = model
        self._dimension = dimension

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        headers = {"Authorization": f"Bearer {self._api_key}"}
        payload = {"model": self._model, "input": texts}
        response = httpx.post(
            f"{self._api_url}/embeddings",
            json=payload,
            headers=headers,
            timeout=60.0,
        )
        response.raise_for_status()
        data = response.json()["data"]
        ordered = sorted(data, key=lambda item: item["index"])
        return [item["embedding"] for item in ordered]


class EmbeddingServiceFactory:
    @staticmethod
    def create() -> EmbeddingService:
        provider = settings.EMBEDDING_PROVIDER.strip().lower()

        if provider == "hash":
            return HashEmbeddingService(dimension=settings.EMBEDDING_DIMENSION)

        if provider in {"huggingface", "hf"}:
            return HuggingFaceEmbeddingService(
                api_key=settings.EMBEDDING_API_KEY,
                model=settings.EMBEDDING_MODEL,
                dimension=settings.EMBEDDING_DIMENSION,
                api_url=settings.EMBEDDING_API_URL,
            )

        if provider == "fastembed":
            return FastEmbedEmbeddingService(model_name=settings.EMBEDDING_MODEL)

        if provider == "http":
            return HttpEmbeddingService(
                api_url=settings.EMBEDDING_API_URL,
                api_key=settings.EMBEDDING_API_KEY,
                model=settings.EMBEDDING_MODEL,
                dimension=settings.EMBEDDING_DIMENSION,
            )

        raise ValueError(
            f"Unsupported embedding provider: {provider}. "
            "Supported values: huggingface, hash, fastembed, http."
        )


@lru_cache(maxsize=1)
def get_embedding_service() -> EmbeddingService:
    return EmbeddingServiceFactory.create()
