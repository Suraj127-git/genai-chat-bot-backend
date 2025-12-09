from typing import Dict, Any
import os
from backend.app.factories.llm_factory import LLMFactory
from backend.app.graph.enhanced_graph_builder import EnhancedGraphBuilder
from backend.app.common.logger import logger

class NewsService:
    def __init__(self, embedding_model: str = "nomic-embed-text"):
        provider = os.getenv("DEFAULT_PROVIDER", "Groq")
        model = os.getenv("DEFAULT_MODEL", "llama3-8b-8192")
        self.llm = LLMFactory.create(provider, model)
        self.graph_builder = EnhancedGraphBuilder(model=self.llm, embedding_model=embedding_model)

    @staticmethod
    def map_timeframe(text: str) -> str:
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

    def run(self, timeframe: str) -> Dict[str, Any]:
        graph = self.graph_builder.setup_graph("AI News")
        frequency = self.map_timeframe(timeframe)
        initial_state = {"messages": [frequency], "user_message": timeframe, "usecase": "AI News"}
        logger.info("news_service")
        return graph.invoke(initial_state)

