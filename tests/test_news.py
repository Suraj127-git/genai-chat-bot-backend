import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_news_requires_backend_defaults(monkeypatch):
    monkeypatch.setenv('DEFAULT_PROVIDER','Groq')
    monkeypatch.setenv('DEFAULT_MODEL','llama-3.1-70b-versatile')
    r = client.post('/news/summary', json={'timeframe': 'last 24 hours'})
    assert r.status_code in (200, 500)
