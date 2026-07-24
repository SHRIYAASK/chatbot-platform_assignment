import json
import uuid
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:8000"


def req(method, path, data=None, headers=None):
    url = BASE + path
    body = None
    h = dict(headers or {})
    if data is not None:
        body = json.dumps(data).encode()
        h["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=body, headers=h, method=method)
    try:
        with urllib.request.urlopen(request) as resp:
            content = resp.read().decode()
            return resp.status, json.loads(content) if content else None
    except urllib.error.HTTPError as exc:
        content = exc.read().decode()
        return exc.code, json.loads(content) if content else None


status, _ = req("GET", "/health")
print("health", status)

email = f"workspace_{uuid.uuid4().hex[:8]}@example.com"
password = "Password123!"
status, _ = req(
    "POST",
    "/auth/register",
    {
        "name": "John Doe",
        "email": email,
        "password": password,
        "confirm_password": password,
    },
)
print("register", status)

status, data = req("POST", "/auth/login", {"email": email, "password": password})
print("login", status)
token = data["access_token"]
headers = {"Authorization": f"Bearer {token}"}

status, _ = req("GET", "/auth/me", headers=headers)
print("me", status)

status, project = req(
    "POST",
    "/projects",
    {
        "title": "Python Tutor",
        "description": "Help with Python coding and optimization.",
    },
    headers=headers,
)
print("create", status, project["title"] if project and "title" in project else project)
print(
    "models",
    project.get("primary_model") if project else None,
    project.get("fallback_model") if project else None,
)

status, listing = req("GET", "/projects", headers=headers)
print("list", status, listing["total"] if listing else None)

status, detail = req("GET", f"/projects/{project['id']}", headers=headers)
print("get", status, detail["title"] if detail else None)

status, updated = req(
    "PUT",
    f"/projects/{project['id']}",
    {
        "title": "Python Tutor Pro",
        "description": "Advanced Python help with performance tuning.",
    },
    headers=headers,
)
print("update", status, updated["title"] if updated else None)

status, _ = req("DELETE", f"/projects/{project['id']}", headers=headers)
print("delete", status)

status, owned = req(
    "POST",
    "/projects",
    {
        "title": "Resume Bot",
        "description": "Help users improve resumes and cover letters.",
    },
    headers=headers,
)
email2 = f"alice_{uuid.uuid4().hex[:8]}@example.com"
req(
    "POST",
    "/auth/register",
    {
        "name": "Alice Smith",
        "email": email2,
        "password": password,
        "confirm_password": password,
    },
)
_, login2 = req("POST", "/auth/login", {"email": email2, "password": password})
headers2 = {"Authorization": f"Bearer {login2['access_token']}"}
status, body = req("GET", f"/projects/{owned['id']}", headers=headers2)
print("forbidden", status, body.get("detail") if body else None)
