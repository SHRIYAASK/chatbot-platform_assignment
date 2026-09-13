import os

from app.core.voice_api_url import resolve_voice_api_base_url


def test_uses_render_port_when_default_localhost(monkeypatch):
    monkeypatch.setenv("RENDER", "true")
    monkeypatch.setenv("PORT", "10000")
    assert resolve_voice_api_base_url("http://127.0.0.1:8002") == "http://127.0.0.1:10000"


def test_substitutes_port_placeholder(monkeypatch):
    monkeypatch.setenv("PORT", "10000")
    assert (
        resolve_voice_api_base_url("http://127.0.0.1:${PORT}")
        == "http://127.0.0.1:10000"
    )


def test_respects_explicit_public_url(monkeypatch):
    monkeypatch.setenv("RENDER", "true")
    monkeypatch.setenv("PORT", "10000")
    url = "https://api.example.onrender.com"
    assert resolve_voice_api_base_url(url) == url


def test_local_default_port(monkeypatch):
    monkeypatch.delenv("RENDER", raising=False)
    monkeypatch.delenv("PORT", raising=False)
    assert resolve_voice_api_base_url("") == "http://127.0.0.1:8002"
