from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PLACEHOLDER_SECRETS = {
    "",
    "change-me-to-a-long-random-secret",
    "changeme",
    "secret",
    "your-secret-key",
}

EMBEDDING_KEY_PLACEHOLDERS = {
    "",
    "your-huggingface-api-key",
    "your-embedding-api-key",
    "hf_your_token_here",
}


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    GROQ_API_KEY: str = ""
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"
    PRIMARY_MODEL: str = "openai/gpt-oss-120b"
    FALLBACK_MODEL: str = "llama-3.3-70b-versatile"

    UPLOAD_DIR: str = "uploads"
    STORAGE_PROVIDER: str = "local"

    # RAG / embeddings
    RAG_ENABLED: bool = True
    RAG_TOP_K: int = 5
    EMBEDDING_PROVIDER: str = "huggingface"
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    EMBEDDING_DIMENSION: int = 384
    EMBEDDING_API_URL: str = "https://router.huggingface.co/hf-inference/models"
    EMBEDDING_API_KEY: str = ""
    USE_PGVECTOR: bool = False

    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"
    MODERATION_ENABLED: bool = True

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_JSON: bool = False

    # Database connection pool
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_RECYCLE: int = 1800
    DB_POOL_TIMEOUT: int = 30

    # Automatically run Alembic migrations on startup (recommended for local dev).
    AUTO_MIGRATE: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @field_validator("CORS_ORIGINS")
    @classmethod
    def parse_cors_origins(cls, value: str) -> str:
        return value.strip()

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, value: str) -> str:
        normalized = (value or "").strip()
        if normalized.lower() in PLACEHOLDER_SECRETS:
            raise ValueError(
                "SECRET_KEY is missing or uses a known placeholder value. "
                "Set a strong, random SECRET_KEY in backend/.env."
            )
        if len(normalized) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long.")
        return normalized

    @model_validator(mode="after")
    def validate_embedding_settings(self) -> "Settings":
        provider = self.EMBEDDING_PROVIDER.strip().lower()
        api_key = self.EMBEDDING_API_KEY.strip()

        if provider in {"huggingface", "hf", "http"}:
            if api_key.lower() in EMBEDDING_KEY_PLACEHOLDERS:
                raise ValueError(
                    "EMBEDDING_API_KEY is required for document search. "
                    "Create a Hugging Face token at https://huggingface.co/settings/tokens "
                    "and set EMBEDDING_API_KEY in backend/.env."
                )
        return self

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.strip().lower() in {"production", "prod"}


settings = Settings()
