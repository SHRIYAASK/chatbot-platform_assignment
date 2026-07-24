from uuid import uuid4


def _register_payload():
    email = f"user_{uuid4().hex[:8]}@example.com"
    password = "Passw0rd!"
    return email, password, {
        "name": "Jane Doe",
        "email": email,
        "password": password,
        "confirm_password": password,
    }


def test_register_and_login(client):
    email, password, payload = _register_payload()

    register = client.post("/auth/register", json=payload)
    assert register.status_code == 201
    body = register.json()
    assert body["email"] == email
    assert "hashed_password" not in body

    login = client.post("/auth/login", json={"email": email, "password": password})
    assert login.status_code == 200
    assert login.json()["token_type"] == "bearer"


def test_duplicate_email_rejected(client):
    _, _, payload = _register_payload()
    assert client.post("/auth/register", json=payload).status_code == 201
    duplicate = client.post("/auth/register", json=payload)
    assert duplicate.status_code == 409


def test_password_mismatch_rejected(client):
    _, _, payload = _register_payload()
    payload["confirm_password"] = "Different1!"
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 422


def test_weak_password_rejected(client):
    email = f"user_{uuid4().hex[:8]}@example.com"
    response = client.post(
        "/auth/register",
        json={
            "name": "Weak Pass",
            "email": email,
            "password": "weakpass",
            "confirm_password": "weakpass",
        },
    )
    assert response.status_code == 422


def test_invalid_login(client):
    response = client.post(
        "/auth/login",
        json={"email": "nobody@example.com", "password": "Passw0rd!"},
    )
    assert response.status_code == 401


def test_me_requires_auth(client):
    assert client.get("/auth/me").status_code in (401, 403)


def test_me_returns_current_user(client, auth_headers):
    response = client.get("/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert "email" in response.json()
