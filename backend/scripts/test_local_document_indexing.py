"""Run document indexing locally against Postgres/HF to reproduce failures."""

import io
import os
import sys
import time
import uuid

# Use real HF provider from .env
os.environ.setdefault("EMBEDDING_PROVIDER", "huggingface")

from fastapi.testclient import TestClient  # noqa: E402

import app.main as main_module  # noqa: E402


def main():
    email = f"doc_{uuid.uuid4().hex[:8]}@example.com"
    password = "Passw0rd!"

    with TestClient(main_module.app) as client:
        client.post(
            "/auth/register",
            json={
                "name": "Doc Local",
                "email": email,
                "password": password,
                "confirm_password": password,
            },
        )
        token = client.post("/auth/login", json={"email": email, "password": password}).json()[
            "access_token"
        ]
        headers = {"Authorization": f"Bearer {token}"}

        project_id = client.post(
            "/projects",
            json={"title": f"Local {uuid.uuid4().hex[:6]}", "description": "Local doc test project."},
            headers=headers,
        ).json()["id"]

        upload = client.post(
            f"/projects/{project_id}/documents",
            files={"file": ("notes.txt", io.BytesIO(b"Refund policy allows returns within 30 days."), "text/plain")},
            headers=headers,
        )
        print("upload:", upload.status_code, upload.text[:160])

        for i in range(10):
            docs = client.get(f"/projects/{project_id}/documents", headers=headers).json()["documents"]
            status = docs[0]["status"] if docs else "missing"
            print(f"poll {i}: {status}")
            if status != "processing":
                break
            time.sleep(1)


if __name__ == "__main__":
    main()
