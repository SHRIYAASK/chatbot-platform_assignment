def _create_project(client, headers, title="My Bot", description="A helpful assistant bot."):
    return client.post(
        "/projects",
        json={"title": title, "description": description},
        headers=headers,
    )


def test_create_and_list_project(client, auth_headers):
    created = _create_project(client, auth_headers)
    assert created.status_code == 201
    project = created.json()
    assert project["title"] == "My Bot"
    assert project["primary_model"]
    assert project["created_at"]
    assert project["summary"] == {
        "messages": 0,
        "conversations": 0,
        "documents": 0,
        "storage_mb": 0.0,
        "model": "GPT OSS 120B",
    }

    listing = client.get("/projects", headers=auth_headers)
    assert listing.status_code == 200
    payload = listing.json()
    assert payload["total"] >= 1
    listed = next(item for item in payload["projects"] if item["id"] == project["id"])
    assert listed["summary"]["messages"] == 0
    assert listed["summary"]["model"] == "GPT OSS 120B"


def test_project_summary_counts(client, auth_headers):
    project_id = _create_project(client, auth_headers, title="Summary Bot").json()["id"]

    conversation = client.post(
        f"/projects/{project_id}/conversations",
        json={"title": "First chat"},
        headers=auth_headers,
    )
    assert conversation.status_code == 201

    listing = client.get("/projects", headers=auth_headers)
    assert listing.status_code == 200
    project = next(item for item in listing.json()["projects"] if item["id"] == project_id)
    summary = project["summary"]

    assert summary["conversations"] == 1
    assert summary["messages"] == 0
    assert summary["documents"] == 0
    assert summary["storage_mb"] == 0.0
    assert summary["model"] == "GPT OSS 120B"


def test_duplicate_title_conflict(client, auth_headers):
    _create_project(client, auth_headers, title="Unique Bot")
    duplicate = _create_project(client, auth_headers, title="Unique Bot")
    assert duplicate.status_code == 409


def test_get_update_delete_project(client, auth_headers):
    created = _create_project(client, auth_headers, title="Lifecycle Bot")
    project_id = created.json()["id"]

    got = client.get(f"/projects/{project_id}", headers=auth_headers)
    assert got.status_code == 200

    updated = client.put(
        f"/projects/{project_id}",
        json={"title": "Lifecycle Bot v2", "description": "Updated description here."},
        headers=auth_headers,
    )
    assert updated.status_code == 200
    assert updated.json()["title"] == "Lifecycle Bot v2"

    deleted = client.delete(f"/projects/{project_id}", headers=auth_headers)
    assert deleted.status_code == 204

    missing = client.get(f"/projects/{project_id}", headers=auth_headers)
    assert missing.status_code == 404


def test_project_requires_auth(client):
    assert client.get("/projects").status_code in (401, 403)


def test_cannot_access_other_users_project(client, auth_headers):
    created = _create_project(client, auth_headers, title="Private Bot")
    project_id = created.json()["id"]

    # Second user
    from uuid import uuid4

    email = f"user_{uuid4().hex[:8]}@example.com"
    password = "Passw0rd!"
    client.post(
        "/auth/register",
        json={
            "name": "Other User",
            "email": email,
            "password": password,
            "confirm_password": password,
        },
    )
    login = client.post("/auth/login", json={"email": email, "password": password})
    other_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = client.get(f"/projects/{project_id}", headers=other_headers)
    assert response.status_code == 403


def test_prompt_crud(client, auth_headers):
    project_id = _create_project(client, auth_headers, title="Prompt Bot").json()["id"]

    created = client.post(
        f"/projects/{project_id}/prompts",
        json={"content": "You are a concise assistant."},
        headers=auth_headers,
    )
    assert created.status_code == 201
    prompt_id = created.json()["id"]

    listing = client.get(f"/projects/{project_id}/prompts", headers=auth_headers)
    assert listing.status_code == 200
    assert listing.json()["total"] >= 1

    deleted = client.delete(
        f"/projects/{project_id}/prompts/{prompt_id}", headers=auth_headers
    )
    assert deleted.status_code == 204
