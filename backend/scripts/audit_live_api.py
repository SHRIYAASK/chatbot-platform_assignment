"""Audit every deployed endpoint and report status codes plus CORS headers.

Usage:
    python scripts/audit_live_api.py [base_url] [origin]
"""

import json
import sys
import uuid

import httpx

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "https://chatbot-platform-assignment-gcfp.onrender.com"
ORIGIN = sys.argv[2] if len(sys.argv) > 2 else "https://chatbot-platform-assignment.vercel.app"

HEADERS = {"Origin": ORIGIN, "Content-Type": "application/json"}
results: list[tuple[str, str, int, bool, str]] = []


def record(method: str, path: str, response: httpx.Response) -> None:
    cors = "access-control-allow-origin" in response.headers
    body = response.text[:180].replace("\n", " ")
    results.append((method, path, response.status_code, cors, body))


def main() -> None:
    email = f"audit_{uuid.uuid4().hex[:10]}@example.com"
    password = "Passw0rd!"

    with httpx.Client(base_url=BASE_URL, timeout=60.0) as client:
        for path in ("/", "/health", "/health/live", "/health/ready"):
            record("GET", path, client.get(path, headers=HEADERS))

        record("OPTIONS", "/auth/register", client.request(
            "OPTIONS", "/auth/register",
            headers={**HEADERS, "Access-Control-Request-Method": "POST"},
        ))

        register_payload = {
            "name": "Audit User",
            "email": email,
            "password": password,
            "confirm_password": password,
        }
        record("POST", "/auth/register", client.post(
            "/auth/register", json=register_payload, headers=HEADERS
        ))
        record("POST", "/auth/register (duplicate)", client.post(
            "/auth/register", json=register_payload, headers=HEADERS
        ))
        record("POST", "/auth/register (weak pw)", client.post(
            "/auth/register",
            json={**register_payload, "email": f"x{email}", "password": "weakpass", "confirm_password": "weakpass"},
            headers=HEADERS,
        ))

        login = client.post(
            "/auth/login", json={"email": email, "password": password}, headers=HEADERS
        )
        record("POST", "/auth/login", login)
        if login.status_code != 200:
            print_results()
            sys.exit("Login failed; cannot audit authenticated routes.")

        token = login.json()["access_token"]
        auth = {**HEADERS, "Authorization": f"Bearer {token}"}

        record("GET", "/auth/me", client.get("/auth/me", headers=auth))
        record("GET", "/projects (no auth)", client.get("/projects", headers=HEADERS))
        record("GET", "/projects", client.get("/projects", headers=auth))

        project_payload = {
            "title": f"Audit {uuid.uuid4().hex[:6]}",
            "description": "Automated audit project for deployment verification.",
        }
        created = client.post("/projects", json=project_payload, headers=auth)
        record("POST", "/projects", created)
        record("POST", "/projects (duplicate)", client.post(
            "/projects", json=project_payload, headers=auth
        ))
        record("POST", "/projects (invalid)", client.post(
            "/projects", json={"title": "x", "description": "short"}, headers=auth
        ))

        if created.status_code != 201:
            print_results()
            sys.exit("Project creation failed; cannot audit project routes.")

        pid = created.json()["id"]
        record("GET", f"/projects/{pid}", client.get(f"/projects/{pid}", headers=auth))
        record("GET", "/projects/999999", client.get("/projects/999999", headers=auth))
        record("PUT", f"/projects/{pid}", client.put(
            f"/projects/{pid}",
            json={**project_payload, "description": "Updated audit description text."},
            headers=auth,
        ))
        record("GET", f"/projects/{pid}/prompts", client.get(f"/projects/{pid}/prompts", headers=auth))
        record("GET", f"/projects/{pid}/documents", client.get(f"/projects/{pid}/documents", headers=auth))
        record("GET", f"/projects/{pid}/files", client.get(f"/projects/{pid}/files", headers=auth))
        record("GET", f"/projects/{pid}/conversations", client.get(
            f"/projects/{pid}/conversations", headers=auth
        ))
        record("GET", f"/projects/{pid}/messages", client.get(
            f"/projects/{pid}/messages", headers=auth
        ))

        convo = client.post(
            f"/projects/{pid}/conversations", json={"title": "Audit chat"}, headers=auth
        )
        record("POST", f"/projects/{pid}/conversations", convo)
        if convo.status_code in (200, 201):
            cid = convo.json()["id"]
            record("GET", f"/projects/{pid}/conversations/{cid}/messages", client.get(
                f"/projects/{pid}/conversations/{cid}/messages", headers=auth
            ))
            record("POST", f"/projects/{pid}/conversations/{cid}/messages", client.post(
                f"/projects/{pid}/conversations/{cid}/messages",
                json={"content": "Hello, this is an automated audit message."},
                headers=auth,
            ))

        record("DELETE", f"/projects/{pid}", client.delete(f"/projects/{pid}", headers=auth))

    print_results()


def print_results() -> None:
    print(f"\n{'METHOD':7} {'PATH':48} {'CODE':5} {'CORS':5} BODY")
    print("-" * 130)
    for method, path, code, cors, body in results:
        flag = "yes" if cors else "NO"
        print(f"{method:7} {path:48} {code:<5} {flag:5} {body}")

    failures = [r for r in results if r[2] >= 500 or not r[3]]
    print(f"\nTotal checks: {len(results)} | Problems: {len(failures)}")
    for method, path, code, cors, body in failures:
        reason = "5xx" if code >= 500 else "missing CORS header"
        print(f"  - {method} {path} -> {code} ({reason}) {body}")


if __name__ == "__main__":
    main()
