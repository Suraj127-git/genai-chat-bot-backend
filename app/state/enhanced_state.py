from typing import List, Dict, Any, Optional
from langgraph.graph import MessagesState
from .state import State

class EnhancedState(State):
    vector_search_results: Optional[List[Dict[str, Any]]] = None
    from_cache: bool = False
    cache_hit_score: float = 0.0
    similarity_threshold: float = 0.8
    vector_search_limit: int = 5
    usecase: str = "Basic Chatbot"
    embedding_model: str = "nomic-embed-text"
    news_sources: Optional[List[str]] = None
    summary_length: str = "Detailed"
    timeframe: str = "last 24 hours"

