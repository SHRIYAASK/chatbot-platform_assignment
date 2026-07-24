from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)
email = f"tc_{uuid.uuid4().hex[:6]}@test.com"
pwd = "Password123!"
client.post(
    "/auth/register",
    json={"name": "TC User", "email": email, "password": pwd, "confirm_password": pwd},
)
login = client.post("/auth/login", json={"email": email, "password": pwd}).json()
headers = {"Authorization": f"Bearer {login['access_token']}"}
proj = client.post(
    "/projects",
    json={"title": "TC Bot", "description": "Test assistant for chat module."},
    headers=headers,
).json()
response = client.post(
    f"/projects/{proj['id']}/messages",
    json={"content": "what is a list?"},
    headers=headers,
)
print("status", response.status_code)
print("body", response.json())
