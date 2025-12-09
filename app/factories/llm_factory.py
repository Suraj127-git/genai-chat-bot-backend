import os
from fastapi import HTTPException
from langchain_groq import ChatGroq
from langchain_community.chat_models import ChatOllama
from backend.app.common.logger import logger

class LLMFactory:
    @staticmethod
    def create(provider: str, model: str):
        p = provider.lower()
        if p == "groq":
            api_key = os.getenv("GROQ_API_KEY", "")
            if not api_key:
                raise HTTPException(status_code=400, detail="Missing GROQ_API_KEY")
            logger.info(f"llm_factory groq {model}")
            return ChatGroq(api_key=api_key, model=model)
        if p == "ollama":
            logger.info(f"llm_factory ollama {model}")
            return ChatOllama(model=model)
        raise HTTPException(status_code=400, detail="Invalid provider")

