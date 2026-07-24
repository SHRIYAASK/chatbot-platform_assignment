"""RAG document upload and retrieval tests."""

import io

from docx import Document as DocxDocument


def _create_project(client, auth_headers, title="RAG Project"):
    response = client.post(
        "/projects",
        json={"title": title, "description": "Answer using uploaded documents."},
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_list_documents_empty(client, auth_headers):
    project_id = _create_project(client, auth_headers, "Empty Docs")

    response = client.get(f"/projects/{project_id}/documents", headers=auth_headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 0
    assert payload["documents"] == []


def test_upload_and_delete_text_document(client, auth_headers):
    project_id = _create_project(client, auth_headers, "Upload Docs")

    files = {
        "file": ("notes.txt", io.BytesIO(b"Project alpha launch is scheduled for July."), "text/plain"),
    }
    upload = client.post(
        f"/projects/{project_id}/documents",
        files=files,
        headers=auth_headers,
    )
    assert upload.status_code == 201, upload.text
    payload = upload.json()
    assert payload["document"]["filename"] == "notes.txt"
    assert payload["document"]["status"] == "processing"
    assert payload["chunks_indexed"] == 0

    listing = client.get(f"/projects/{project_id}/documents", headers=auth_headers)
    assert listing.status_code == 200
    assert listing.json()["total"] == 1
    assert listing.json()["documents"][0]["status"] == "ready"

    document_id = payload["document"]["id"]
    delete = client.delete(
        f"/projects/{project_id}/documents/{document_id}",
        headers=auth_headers,
    )
    assert delete.status_code == 204

    listing_after = client.get(f"/projects/{project_id}/documents", headers=auth_headers)
    assert listing_after.json()["total"] == 0


def test_upload_docx_document(client, auth_headers):
    project_id = _create_project(client, auth_headers, "DOCX Docs")

    buffer = io.BytesIO()
    document = DocxDocument()
    document.add_paragraph("The refund policy allows returns within 30 days.")
    document.save(buffer)
    buffer.seek(0)

    files = {
        "file": (
            "policy.docx",
            buffer,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ),
    }
    upload = client.post(
        f"/projects/{project_id}/documents",
        files=files,
        headers=auth_headers,
    )
    assert upload.status_code == 201, upload.text

    listing = client.get(f"/projects/{project_id}/documents", headers=auth_headers)
    assert listing.json()["documents"][0]["status"] == "ready"


def test_upload_rejects_empty_file(client, auth_headers):
    project_id = _create_project(client, auth_headers, "Invalid Docs")

    files = {"file": ("empty.txt", io.BytesIO(b""), "text/plain")}
    upload = client.post(
        f"/projects/{project_id}/documents",
        files=files,
        headers=auth_headers,
    )
    assert upload.status_code == 400
