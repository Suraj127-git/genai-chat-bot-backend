from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import time
from dotenv import load_dotenv
from backend.app.common.logger import logger
from backend.app.factories.llm_factory import LLMFactory
from backend.app.services.chat_service import ChatService
from backend.app.services.news_service import NewsService
from backend.app.repositories.chroma_repository import ChromaRepository
from .instrumentation import configure_observability

load_dotenv()

configure_observability()
app = FastAPI(
    title="Agentic AI Chatbot API",
    version="0.1.0",
    description="FastAPI backend for GenAI Chatbot with ChromaDB and LangGraph"
)

# Configure CORS for Railway deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    provider: str
    model: str
    usecase: str
    message: str
    embedding_model: Optional[str] = "nomic-embed-text"


class ChatResponse(BaseModel):
    content: str
    from_cache: bool = False


class NewsRequest(BaseModel):
    timeframe: str
    embedding_model: Optional[str] = "nomic-embed-text"


class NewsResponse(BaseModel):
    summary: str
    saved_file: Optional[str] = None
    from_cache: bool = False


class HealthResponse(BaseModel):
    status: str
    timestamp: float
    uptime: float
    version: str
    services: Dict[str, str]


# Application startup time
start_time = time.time()


@app.get("/health", response_model=HealthResponse)
def health():
    """Comprehensive health check endpoint"""
    try:
        # Test ChromaDB connection
        chroma_status = "healthy"
        try:
            chroma_repo = ChromaRepository()
            chroma_repo.stats()
        except Exception as e:
            chroma_status = f"unhealthy: {str(e)}"
            logger.warning(f"ChromaDB health check failed: {e}")
        
        # Test environment variables
        env_status = "healthy"
        required_vars = ["GROQ_API_KEY", "OPENAI_API_KEY", "TAVILY_API_KEY"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            env_status = f"warning: missing {', '.join(missing_vars)}"
        
        uptime = time.time() - start_time
        
        return HealthResponse(
            status="ok" if chroma_status == "healthy" else "degraded",
            timestamp=time.time(),
            uptime=uptime,
            version="0.1.0",
            services={
                "chroma_db": chroma_status,
                "environment": env_status,
                "api": "healthy"
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {e}")


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    try:
        service = ChatService(provider=req.provider, model=req.model, embedding_model=req.embedding_model)
        result = service.run(req.usecase, req.message)
        if req.usecase == "AI News":
            raise HTTPException(status_code=400, detail="Use /news/summary for AI News")
        messages = result.get("messages")
        if hasattr(messages, "content"):
            content = messages.content
        elif isinstance(messages, list) and len(messages) > 0:
            last = messages[-1]
            content = last.content if hasattr(last, "content") else str(last)
        else:
            content = str(messages)
        from_cache = False
        if isinstance(content, str) and "[This response was retrieved from previous similar questions]" in content:
            from_cache = True
        return ChatResponse(content=content, from_cache=from_cache)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def map_timeframe_to_frequency(text: str) -> str:
    t = text.lower()
    if "24" in t or "day" in t:
        return "daily"
    if "week" in t or "7" in t:
        return "weekly"
    if "month" in t or "30" in t:
        return "monthly"
    if "year" in t or "365" in t:
        return "year"
    return "daily"


@app.post("/news/summary", response_model=NewsResponse)
def news_summary(req: NewsRequest):
    try:
        service = NewsService(embedding_model=req.embedding_model)
        result = service.run(req.timeframe)
        summary = result.get("summary", "")
        saved_file = result.get("filename") or result.get("saved_file")
        from_cache = result.get("from_cache", False)
        return NewsResponse(summary=summary, saved_file=saved_file, from_cache=from_cache)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"News summary error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def root():
    return {"message": "Agentic AI Chatbot API", "version": "0.1.0", "status": "running"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port)