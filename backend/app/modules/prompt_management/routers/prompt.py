from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.authentication.models.user import User
from app.modules.prompt_management.schemas.prompt import (
    PromptCreate,
    PromptListResponse,
    PromptResponse,
    PromptUpdate,
)
from app.modules.prompt_management.services.prompt_service import PromptService

router = APIRouter(prefix="/projects/{project_id}/prompts", tags=["Prompt Management"])


@router.post("", response_model=PromptResponse, status_code=status.HTTP_201_CREATED)
def create_prompt(
    project_id: int,
    prompt_data: PromptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return PromptService.create_prompt(db, current_user, project_id, prompt_data)


@router.get("", response_model=PromptListResponse)
def list_prompts(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    prompts = PromptService.list_prompts(db, current_user, project_id)
    return PromptListResponse(total=len(prompts), prompts=prompts)


@router.get("/{prompt_id}", response_model=PromptResponse)
def get_prompt(
    project_id: int,
    prompt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return PromptService.get_prompt(db, current_user, project_id, prompt_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found.")


@router.put("/{prompt_id}", response_model=PromptResponse)
def update_prompt(
    project_id: int,
    prompt_id: int,
    prompt_data: PromptUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return PromptService.update_prompt(
            db,
            current_user,
            project_id,
            prompt_id,
            prompt_data,
        )
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found.")


@router.delete("/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prompt(
    project_id: int,
    prompt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        PromptService.delete_prompt(db, current_user, project_id, prompt_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found.")

    return None
