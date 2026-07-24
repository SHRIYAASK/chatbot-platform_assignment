from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.chat.services.retrieval_service import RetrievalService
from app.modules.chat.services.upload_service import UploadService
from app.shared.rag.embedding_service import get_embedding_service
from app.shared.storage.storage_factory import get_storage_service


def get_upload_service() -> UploadService:
    return UploadService(
        storage=get_storage_service(),
        embedding_service=get_embedding_service(),
    )


def get_retrieval_service(db: Session = Depends(get_db)) -> RetrievalService:
    return RetrievalService(db=db, embedding_service=get_embedding_service())
