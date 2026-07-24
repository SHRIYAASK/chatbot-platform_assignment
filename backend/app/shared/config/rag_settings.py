"""RAG configuration constants."""

PARENT_CHUNK_MIN_TOKENS = 1000
PARENT_CHUNK_MAX_TOKENS = 1500
PARENT_CHUNK_TARGET_TOKENS = 1200

CHILD_CHUNK_MIN_TOKENS = 200
CHILD_CHUNK_MAX_TOKENS = 300
CHILD_CHUNK_TARGET_TOKENS = 250

DEFAULT_TOP_K = 5
MAX_CONTEXT_CHARS = 12000

ALLOWED_EXTENSIONS = {".txt", ".pdf", ".md", ".json", ".docx"}
ALLOWED_CONTENT_TYPES = {
    "text/plain",
    "application/pdf",
    "text/markdown",
    "application/json",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024
READ_CHUNK_SIZE = 1024 * 1024

FILE_SIGNATURES: dict[str, tuple[bytes, ...]] = {
    ".pdf": (b"%PDF-",),
    ".json": (b"{", b"["),
    ".docx": (b"PK\x03\x04",),
}
