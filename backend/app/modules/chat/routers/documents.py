from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.service_dependencies import get_upload_service
from app.modules.authentication.models.user import User
from app.modules.chat.schemas.document import (
    DocumentListResponse,
    DocumentResponse,
    DocumentUploadResponse,
)
from app.modules.chat.services.upload_service import UploadService

router = APIRouter(prefix="/projects/{project_id}/documents", tags=["Chat Documents"])


@router.get("", response_model=DocumentListResponse)
def list_documents(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    upload_service: UploadService = Depends(get_upload_service),
):
    documents = upload_service.list_documents(db, current_user, project_id)
    return DocumentListResponse(
        total=len(documents),
        documents=[DocumentResponse.model_validate(document) for document in documents],
    )


@router.post("", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    project_id: int,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    upload_service: UploadService = Depends(get_upload_service),
):
    try:
        document, content = await upload_service.upload_document(
            db,
            current_user,
            project_id,
            file,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    background_tasks.add_task(UploadService.index_document, document.id, content)

    return DocumentUploadResponse(
        document=DocumentResponse.model_validate(document),
        chunks_indexed=0,
    )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    project_id: int,
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    upload_service: UploadService = Depends(get_upload_service),
):
    try:
        await upload_service.delete_document(db, current_user, project_id, document_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    return None
