"""Shared project authorization helper.

Centralizes ownership checks so every module (chat, prompts, files, workspace)
depends on shared infrastructure rather than on the workspace feature module.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.authentication.models.user import User
from app.modules.workspace.models.project import Project


def get_owned_project_or_403(
    db: Session,
    project_id: int,
    current_user: User,
) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found.",
        )

    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this project.",
        )

    return project
