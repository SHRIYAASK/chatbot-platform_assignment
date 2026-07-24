from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from app.core.config import settings
from app.core.database import engine
from app.core.exception_handlers import register_exception_handlers
from app.core.logging_config import configure_logging
from app.core.rate_limit import limiter
from app.modules.authentication.models.user import User  # noqa: F401
from app.modules.authentication.routers.auth import router as auth_router
from app.modules.chat.models.chat_message import ChatMessage  # noqa: F401
from app.modules.chat.models.conversation import Conversation  # noqa: F401
from app.modules.chat.models.document import Document  # noqa: F401
from app.modules.chat.models.document_chunk import DocumentChunk  # noqa: F401
from app.modules.chat.routers.chat import router as chat_router
from app.modules.chat.routers.conversations import router as conversations_router
from app.modules.chat.routers.documents import router as documents_router
from app.modules.file_upload.models.file import ProjectFile  # noqa: F401
from app.modules.prompt_management.models.prompt import Prompt  # noqa: F401
from app.modules.prompt_management.routers.prompt import router as prompt_router
from app.modules.workspace.models.project import Project  # noqa: F401
from app.modules.workspace.routers.project import router as project_router
from app.shared.guardrails.moderation.models import ModerationEvent  # noqa: F401

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.core.migrations import upgrade_head
    from app.modules.chat.services.llm_service import LLMService

    configure_logging()

    if settings.AUTO_MIGRATE:
        try:
            upgrade_head()
        except Exception:
            logger.exception("Automatic database migration failed.")
            raise

    yield
    await LLMService.close()


app = FastAPI(
    title="Chatbot Platform API",
    description="Modular monolith API for the AI Chatbot Platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)


@app.get("/")
def root():
    return {"message": "Chatbot Platform API is running"}


@app.get("/health")
def health_check():
    """Deep health check: verifies database connectivity."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except OperationalError:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "database": "down"},
        )
    return {"status": "healthy", "database": "up"}


@app.get("/health/live")
def liveness():
    """Liveness probe: process is up and serving."""
    return {"status": "alive"}


@app.get("/health/ready")
def readiness():
    """Readiness probe: dependencies (database) are reachable."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except OperationalError:
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "database": "down"},
        )
    return {"status": "ready", "database": "up"}


app.include_router(auth_router)
app.include_router(project_router)
app.include_router(prompt_router)
app.include_router(chat_router)
app.include_router(conversations_router)
app.include_router(documents_router)
