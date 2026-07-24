"""Quick live test for document upload + background indexing."""

import io
import sys
import time
import uuid

import httpx

BASE = sys.argv[1] if len(sys.argv) > 1 else "https://chatbot-platform-assignment-gcfp.onrender.com"
ORIGIN = "https://chatbot-platform-assignment.vercel.app"
headers = {"Origin": ORIGIN}


def poll_status(client, project_id, auth, filename, attempts=20):
    for i in range(attempts):
        docs = client.get(f"/projects/{project_id}/documents", headers=auth).json()["documents"]
        doc = next((d for d in docs if d["filename"] == filename), None)
        if doc:
            print(f"  poll {i}: {filename} -> {doc['status']}")
            if doc["status"] != "processing":
                return doc["status"]
        time.sleep(2)
    return "timeout"


def main():
    email = f"doc_{uuid.uuid4().hex[:8]}@example.com"
    password = "Passw0rd!"

    with httpx.Client(base_url=BASE, timeout=120) as client:
        client.post(
            "/auth/register",
            json={
                "name": "Doc Test",
                "email": email,
                "password": password,
                "confirm_password": password,
            },
            headers=headers,
        )
        token = client.post(
            "/auth/login",
            json={"email": email, "password": password},
            headers=headers,
        ).json()["access_token"]
        auth = {**headers, "Authorization": f"Bearer {token}"}

        project = client.post(
            "/projects",
            json={
                "title": f"Doc {uuid.uuid4().hex[:6]}",
                "description": "Document upload audit project for testing.",
            },
            headers=auth,
        )
        print("Create project:", project.status_code, project.text[:120])
        project_id = project.json()["id"]

        txt = client.post(
            f"/projects/{project_id}/documents",
            files={
                "file": (
                    "notes.txt",
                    io.BytesIO(b"Our refund policy allows returns within 30 days."),
                    "text/plain",
                )
            },
            headers=auth,
        )
        print("TXT upload:", txt.status_code, txt.text[:160])
        print("TXT final status:", poll_status(client, project_id, auth, "notes.txt"))

        pdf_bytes = (
            b"%PDF-1.1\n"
            b"1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj\n"
            b"2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1 >>endobj\n"
            b"3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Contents 4 0 R /Resources<< /Font<< /F1 5 0 R >> >> >>endobj\n"
            b"4 0 obj<< /Length 44 >>stream\n"
            b"BT /F1 24 Tf 72 720 Td (Hello PDF world) Tj ET\n"
            b"endstream endobj\n"
            b"5 0 obj<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>endobj\n"
            b"xref\n0 6\n0000000000 65535 f \n"
            b"trailer<< /Size 6 /Root 1 0 R >>\nstartxref\n0\n%%EOF"
        )
        pdf = client.post(
            f"/projects/{project_id}/documents",
            files={"file": ("sample.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
            headers=auth,
        )
        print("PDF upload:", pdf.status_code, pdf.text[:160])
        print("PDF final status:", poll_status(client, project_id, auth, "sample.pdf"))


if __name__ == "__main__":
    main()
