import os
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_chat_invalid_provider():
    r = client.post('/chat', json={
        'provider': 'Invalid', 'model': 'x', 'usecase': 'Basic Chatbot', 'message': 'Hello'
    })
    assert r.status_code == 400

