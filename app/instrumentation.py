import os
from .common.logger import logger

def configure_observability():
    api_key = os.getenv('LANGCHAIN_API_KEY')
    if api_key:
        os.environ.setdefault('LANGCHAIN_TRACING_V2', 'true')
        os.environ.setdefault('LANGCHAIN_ENDPOINT', 'https://api.smith.langchain.com')
        os.environ.setdefault('LANGCHAIN_PROJECT', os.getenv('LANGCHAIN_PROJECT', 'genai-chat-bot'))
        logger.info('LangSmith tracing enabled')
    else:
        logger.info('LangSmith tracing disabled (no API key)')
