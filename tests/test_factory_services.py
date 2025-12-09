import os
import pytest
from fastapi import HTTPException
from backend.app.factories.llm_factory import LLMFactory
from backend.app.services.chat_service import ChatService

def test_llm_factory_invalid_provider():
    with pytest.raises(HTTPException):
        LLMFactory.create('Invalid','x')

def test_chat_service_init_with_ollama(monkeypatch):
    svc = ChatService(provider='Ollama', model='llama3.2:1b')
    assert svc is not None
