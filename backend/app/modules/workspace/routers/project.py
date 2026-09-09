from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.authentication.models.user import User
from app.modules.chat.services.llm_service import LLMServiceError
from app.modules.workspace.schemas.project import (
    DescriptionRewriteRequest,
    DescriptionRewriteResponse,
    ProjectCreate,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdate,
)
from app.modules.workspace.services.description_rewrite_service import DescriptionRewriteService
from app.modules.workspace.services.project_service import (
    ProjectAlreadyExistsError,
    ProjectService,
)
from app.modules.workspace.services.project_summary_service import ProjectSummaryService

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("/description/rewrite", response_model=DescriptionRewriteResponse)
async def rewrite_project_description(
    payload: DescriptionRewriteRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        rewritten = await DescriptionRewriteService.rewrite_description(payload.description)
    except LLMServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The AI service is temporarily unavailable. Please try again.",
        ) from exc

    return DescriptionRewriteResponse(rewritten_description=rewritten)


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        project = ProjectService.create_project(db, current_user, project_data)
        summary = ProjectSummaryService.get_summary_for_project(db, project)
        return ProjectResponse.model_validate(project).model_copy(update={"summary": summary})
    except ProjectAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Project already exists.",
        )


@router.get("", response_model=ProjectListResponse)
def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    projects = ProjectService.get_all_projects(db, current_user)
    summaries = ProjectSummaryService.get_summaries_for_projects(db, projects)
    project_responses = [
        ProjectResponse.model_validate(project).model_copy(
            update={"summary": summaries[project.id]}
        )
        for project in projects
    ]
    return ProjectListResponse(total=len(project_responses), projects=project_responses)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ProjectService.get_project(db, current_user, project_id)


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return ProjectService.update_project(
            db,
            current_user,
            project_id,
            project_data,
        )
    except ProjectAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Project already exists.",
        )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ProjectService.delete_project(db, current_user, project_id)
    return None
