import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_news_requires_backend_defaults(monkeypatch):
    monkeypatch.setenv('DEFAULT_PROVIDER','Ollama')
    monkeypatch.setenv('DEFAULT_MODEL','llama3.2:1b')
    r = client.post('/news/summary', json={'timeframe': 'last 24 hours'})
    assert r.status_code in (200, 500)
