from unittest.mock import AsyncMock, patch

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.modules.chat.services.llm_types import LLMResult
from app.modules.workspace.models.project import Project


def test_rewrite_requires_auth(client):
    response = client.post(
        "/projects/description/rewrite",
        json={"description": "A helpful assistant for Python tutoring."},
    )
    assert response.status_code in (401, 403)


def test_rewrite_validation(client, auth_headers):
    response = client.post(
        "/projects/description/rewrite",
        json={"description": "short"},
        headers=auth_headers,
    )
    assert response.status_code == 422


@patch(
    "app.modules.workspace.services.description_rewrite_service.LLMService.generate_reply",
    new_callable=AsyncMock,
)
def test_rewrite_returns_rewritten_text(mock_generate, client, auth_headers):
    mock_generate.return_value = LLMResult(
        content="You are a concise Python tutor who explains concepts clearly.",
        model_used="test-model",
        token_count=42,
    )

    response = client.post(
        "/projects/description/rewrite",
        json={"description": "Help users learn Python basics in simple language."},
        headers=auth_headers,
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["rewritten_description"] == (
        "You are a concise Python tutor who explains concepts clearly."
    )
    mock_generate.assert_awaited_once()


@patch(
    "app.modules.workspace.services.description_rewrite_service.LLMService.generate_reply",
    new_callable=AsyncMock,
)
def test_rewrite_does_not_persist_project(mock_generate, client, auth_headers):
    mock_generate.return_value = LLMResult(
        content="Rewritten instructions for the assistant.",
        model_used="test-model",
        token_count=10,
    )

    before = client.get("/projects", headers=auth_headers)
    assert before.status_code == 200
    initial_count = before.json()["total"]

    rewrite = client.post(
        "/projects/description/rewrite",
        json={"description": "Original draft instructions for my assistant."},
        headers=auth_headers,
    )
    assert rewrite.status_code == 200

    after = client.get("/projects", headers=auth_headers)
    assert after.status_code == 200
    assert after.json()["total"] == initial_count

    db: Session = SessionLocal()
    try:
        assert (
            db.query(Project)
            .filter(Project.description == rewrite.json()["rewritten_description"])
            .count()
            == 0
        )
    finally:
        db.close()


@patch(
    "app.modules.workspace.services.description_rewrite_service.LLMService.generate_reply",
    new_callable=AsyncMock,
)
def test_rewrite_llm_unavailable(mock_generate, client, auth_headers):
    from app.modules.chat.services.llm_service import LLMServiceError

    mock_generate.side_effect = LLMServiceError("unavailable")

    response = client.post(
        "/projects/description/rewrite",
        json={"description": "Help users learn Python basics in simple language."},
        headers=auth_headers,
    )
    assert response.status_code == 503
