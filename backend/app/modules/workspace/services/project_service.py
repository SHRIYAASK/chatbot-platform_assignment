from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from app.modules.authentication.models.user import User
from app.modules.workspace.ai_models import (
    get_default_fallback_model,
    get_default_primary_model,
)
from app.shared.authorization.project_access import get_owned_project_or_403
from app.modules.workspace.models.project import Project
from app.modules.workspace.schemas.project import ProjectCreate, ProjectUpdate


class ProjectAlreadyExistsError(Exception):
    pass


def _is_project_title_conflict(exc: IntegrityError) -> bool:
    orig = getattr(exc, "orig", None)
    if orig is not None and getattr(orig, "pgcode", None) == "23505":
        return True

    message = str(orig or exc).lower()
    return "uq_projects_user_id_title" in message or "unique" in message


class ProjectService:
    @staticmethod
    def create_project(
        db: Session,
        current_user: User,
        project_data: ProjectCreate,
    ) -> Project:
        duplicate = (
            db.query(Project)
            .filter(
                Project.user_id == current_user.id,
                Project.title == project_data.title,
            )
            .first()
        )
        if duplicate:
            raise ProjectAlreadyExistsError()

        project = Project(
            user_id=current_user.id,
            title=project_data.title,
            description=project_data.description,
            primary_model=get_default_primary_model(),
            fallback_model=get_default_fallback_model(),
        )

        try:
            db.add(project)
            db.commit()
            db.refresh(project)
        except IntegrityError as exc:
            db.rollback()
            if _is_project_title_conflict(exc):
                raise ProjectAlreadyExistsError() from exc
            raise
        except OperationalError:
            db.rollback()
            raise

        return project

    @staticmethod
    def get_all_projects(db: Session, current_user: User) -> list[Project]:
        return (
            db.query(Project)
            .filter(Project.user_id == current_user.id)
            .order_by(Project.created_at.desc())
            .all()
        )

    @staticmethod
    def get_project(db: Session, current_user: User, project_id: int) -> Project:
        return get_owned_project_or_403(db, project_id, current_user)

    @staticmethod
    def update_project(
        db: Session,
        current_user: User,
        project_id: int,
        project_data: ProjectUpdate,
    ) -> Project:
        project = get_owned_project_or_403(db, project_id, current_user)

        if project.title != project_data.title:
            duplicate = (
                db.query(Project)
                .filter(
                    Project.user_id == current_user.id,
                    Project.title == project_data.title,
                    Project.id != project.id,
                )
                .first()
            )
            if duplicate:
                raise ProjectAlreadyExistsError()

        project.title = project_data.title
        project.description = project_data.description

        try:
            db.commit()
            db.refresh(project)
        except IntegrityError as exc:
            db.rollback()
            if _is_project_title_conflict(exc):
                raise ProjectAlreadyExistsError() from exc
            raise
        except OperationalError:
            db.rollback()
            raise

        return project

    @staticmethod
    def delete_project(
        db: Session,
        current_user: User,
        project_id: int,
    ) -> None:
        project = get_owned_project_or_403(db, project_id, current_user)

        try:
            db.delete(project)
            db.commit()
        except IntegrityError:
            db.rollback()
            raise
        except OperationalError:
            db.rollback()
            raise
