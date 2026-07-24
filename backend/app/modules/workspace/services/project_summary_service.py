"""Lightweight project summary aggregation for the workspace dashboard."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.modules.chat.models.chat_message import ChatMessage
from app.modules.chat.models.conversation import Conversation
from app.modules.chat.models.document import Document
from app.modules.workspace.model_resolver import LEGACY_MODEL_MAP, resolve_project_models
from app.modules.workspace.models.project import Project
from app.modules.workspace.schemas.project import ProjectSummary


MODEL_DISPLAY_NAMES: dict[str, str] = {
    "openai/gpt-oss-120b": "GPT OSS 120B",
    "llama-3.3-70b-versatile": "Llama 3.3 70B",
}


def format_model_display_name(model_id: str) -> str:
    resolved = LEGACY_MODEL_MAP.get(model_id, model_id) or model_id
    if resolved in MODEL_DISPLAY_NAMES:
        return MODEL_DISPLAY_NAMES[resolved]

    slug = resolved.split("/")[-1]
    return slug.replace("-", " ").title()


@dataclass(frozen=True)
class _AggregateCounts:
    messages: int = 0
    conversations: int = 0
    documents: int = 0
    storage_bytes: int = 0


class ProjectSummaryService:
    @staticmethod
    def get_summaries_for_projects(
        db: Session,
        projects: list[Project],
    ) -> dict[int, ProjectSummary]:
        if not projects:
            return {}

        project_ids = [project.id for project in projects]
        aggregates = ProjectSummaryService._load_aggregate_counts(db, project_ids)

        return {
            project.id: ProjectSummaryService._build_summary(project, aggregates[project.id])
            for project in projects
        }

    @staticmethod
    def get_summary_for_project(db: Session, project: Project) -> ProjectSummary:
        aggregates = ProjectSummaryService._load_aggregate_counts(db, [project.id])
        return ProjectSummaryService._build_summary(project, aggregates[project.id])

    @staticmethod
    def _load_aggregate_counts(
        db: Session,
        project_ids: list[int],
    ) -> dict[int, _AggregateCounts]:
        counts = {project_id: _AggregateCounts() for project_id in project_ids}

        message_rows = (
            db.query(ChatMessage.project_id, func.count(ChatMessage.id))
            .filter(ChatMessage.project_id.in_(project_ids))
            .group_by(ChatMessage.project_id)
            .all()
        )
        for project_id, total in message_rows:
            counts[project_id] = _AggregateCounts(
                messages=total,
                conversations=counts[project_id].conversations,
                documents=counts[project_id].documents,
                storage_bytes=counts[project_id].storage_bytes,
            )

        conversation_rows = (
            db.query(Conversation.project_id, func.count(Conversation.id))
            .filter(Conversation.project_id.in_(project_ids))
            .group_by(Conversation.project_id)
            .all()
        )
        for project_id, total in conversation_rows:
            current = counts[project_id]
            counts[project_id] = _AggregateCounts(
                messages=current.messages,
                conversations=total,
                documents=current.documents,
                storage_bytes=current.storage_bytes,
            )

        document_rows = (
            db.query(
                Document.project_id,
                func.count(Document.id),
                func.coalesce(func.sum(Document.file_size), 0),
            )
            .filter(Document.project_id.in_(project_ids))
            .group_by(Document.project_id)
            .all()
        )
        for project_id, total, storage_bytes in document_rows:
            current = counts[project_id]
            counts[project_id] = _AggregateCounts(
                messages=current.messages,
                conversations=current.conversations,
                documents=total,
                storage_bytes=int(storage_bytes or 0),
            )

        return counts

    @staticmethod
    def _build_summary(project: Project, counts: _AggregateCounts) -> ProjectSummary:
        primary_model, _ = resolve_project_models(project.primary_model, project.fallback_model)
        storage_mb = round(counts.storage_bytes / (1024 * 1024), 1)

        return ProjectSummary(
            messages=counts.messages,
            conversations=counts.conversations,
            documents=counts.documents,
            storage_mb=storage_mb,
            model=format_model_display_name(primary_model),
        )
