from sqlalchemy.orm import Session

from app.modules.authentication.models.user import User
from app.modules.prompt_management.models.prompt import Prompt
from app.modules.prompt_management.schemas.prompt import PromptCreate, PromptUpdate
from app.shared.authorization.project_access import get_owned_project_or_403


class PromptService:
    @staticmethod
    def create_prompt(
        db: Session,
        current_user: User,
        project_id: int,
        prompt_data: PromptCreate,
    ) -> Prompt:
        get_owned_project_or_403(db, project_id, current_user)
        prompt = Prompt(project_id=project_id, content=prompt_data.content.strip())
        db.add(prompt)
        db.commit()
        db.refresh(prompt)
        return prompt

    @staticmethod
    def list_prompts(
        db: Session,
        current_user: User,
        project_id: int,
    ) -> list[Prompt]:
        get_owned_project_or_403(db, project_id, current_user)
        return (
            db.query(Prompt)
            .filter(Prompt.project_id == project_id)
            .order_by(Prompt.created_at.desc())
            .all()
        )

    @staticmethod
    def get_prompt(
        db: Session,
        current_user: User,
        project_id: int,
        prompt_id: int,
    ) -> Prompt:
        get_owned_project_or_403(db, project_id, current_user)
        prompt = (
            db.query(Prompt)
            .filter(Prompt.id == prompt_id, Prompt.project_id == project_id)
            .first()
        )
        if prompt is None:
            raise ValueError("Prompt not found.")
        return prompt

    @staticmethod
    def update_prompt(
        db: Session,
        current_user: User,
        project_id: int,
        prompt_id: int,
        prompt_data: PromptUpdate,
    ) -> Prompt:
        prompt = PromptService.get_prompt(db, current_user, project_id, prompt_id)
        prompt.content = prompt_data.content.strip()
        db.commit()
        db.refresh(prompt)
        return prompt

    @staticmethod
    def delete_prompt(
        db: Session,
        current_user: User,
        project_id: int,
        prompt_id: int,
    ) -> None:
        prompt = PromptService.get_prompt(db, current_user, project_id, prompt_id)
        db.delete(prompt)
        db.commit()
