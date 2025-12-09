import os
import pytest
from fastapi import HTTPException
from app.factories.llm_factory import LLMFactory
from app.services.chat_service import ChatService

def test_llm_factory_invalid_provider():
    with pytest.raises(HTTPException):
        LLMFactory.create('Invalid','x')
