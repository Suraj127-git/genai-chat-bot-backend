from typing import Dict, Any
import json
from backend.app.state.state import State
from backend.app.common.logger import logger
from backend.app.repositories.chroma_repository import ChromaRepository
from backend.app.nodes.ai_news_node import AINewsNode

class EnhancedAINewsNode(AINewsNode):
    def __init__(self, model, embedding_model: str = "nomic-embed-text"):
        super().__init__(model)
        self.chroma_repo = ChromaRepository(collection_name="ai_news_collection", embedding_model=embedding_model)
        self.similarity_threshold = 0.75

    def fetch_news(self, state: State) -> Dict[str, Any]:
        logger.info("Enhanced AI News: Fetching news with vector search")
        messages = state.get('messages', [])
        if messages:
            user_query = messages[-1].content if hasattr(messages[-1], 'content') else str(messages[-1])
        else:
            user_query = state.get('user_message', 'latest AI news')
        similar_requests = self.chroma_repo.search(query=user_query, usecase="AI News", limit=3, score_threshold=self.similarity_threshold)
        if similar_requests:
            logger.info(f"Found similar news request with score: {similar_requests[0]['score']}")
            cached_news = similar_requests[0]['answer']
            try:
                if isinstance(cached_news, str) and cached_news.startswith('{'):
                    cached_data = json.loads(cached_news)
                    return {"news_data": cached_data, "from_cache": True}
            except json.JSONDecodeError:
                logger.warning("Could not parse cached news data")
        result = super().fetch_news(state)
        news_data = result.get('news_data', {})
        self.chroma_repo.store(
            question=user_query,
            answer=json.dumps(news_data) if news_data else "No news data available",
            usecase="AI News",
            metadata={"type": "news_fetch", "from_cache": False}
        )
        return result

    def summarize_news(self, state: State) -> Dict[str, Any]:
        logger.info("Enhanced AI News: Summarizing news")
        from_cache = state.get('from_cache', False)
        if from_cache:
            logger.info("Processing cached news data")
        result = super().summarize_news(state)
        summary = result.get('summary', '')
        if summary:
            news_data = state.get('news_data', {})
            query = f"AI news summary for {news_data.get('timeframe', 'recent')}"
            self.chroma_repo.store(question=query, answer=summary, usecase="AI News", metadata={"type": "news_summary", "from_cache": from_cache})
        return result

