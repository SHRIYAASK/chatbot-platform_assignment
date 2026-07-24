import httpx

from app.core.config import settings

text = "hello world test embedding"
headers = {
    "Authorization": f"Bearer {settings.EMBEDDING_API_KEY}",
    "Content-Type": "application/json",
}
payload = {"inputs": text}

base = settings.EMBEDDING_API_URL.rstrip("/")
model = settings.EMBEDDING_MODEL
urls = [
    f"{base}/{model}",
    f"{base}/{model}/pipeline/feature-extraction",
    f"https://api-inference.huggingface.co/pipeline/feature-extraction/{model}",
]

for url in urls:
    try:
        response = httpx.post(url, json=payload, headers=headers, timeout=60)
        print(url)
        print(" ", response.status_code, response.text[:200].replace("\n", " "))
    except Exception as exc:
        print(url)
        print(" ", "ERR", exc)
