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
        try:
            return exc.code, json.loads(content) if content else None
        except json.JSONDecodeError:
            return exc.code, content


email = f"chat_{uuid.uuid4().hex[:6]}@test.com"
pwd = "Password123!"
req("POST", "/auth/register", {"name": "Chat User", "email": email, "password": pwd, "confirm_password": pwd})
_, login = req("POST", "/auth/login", {"email": email, "password": pwd})
token = login["access_token"]
headers = {"Authorization": f"Bearer {token}"}

_, project = req(
    "POST",
    "/projects",
    {
        "title": "Python Tutor",
        "description": "Help with Python coding and optimization.",
    },
    headers=headers,
)
pid = project["id"]
print("project", pid)

status, messages = req("GET", f"/projects/{pid}/messages", headers=headers)
print("list messages", status, messages)

status, sent = req(
    "POST",
    f"/projects/{pid}/messages",
    {"content": "Hello, what can you help me with?"},
    headers=headers,
)
print("send", status, sent)

status, messages = req("GET", f"/projects/{pid}/messages", headers=headers)
print("history count", messages.get("total") if isinstance(messages, dict) else messages)
