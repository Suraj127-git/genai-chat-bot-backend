from typing import Dict, Any
from langchain_core.messages import HumanMessage
from ..factories.llm_factory import LLMFactory
from ..graph.enhanced_graph_builder import EnhancedGraphBuilder
from ..common.logger import logger

class ChatService:
    def __init__(self, provider: str, model: str, embedding_model: str = "nomic-embed-text"):
        self.llm = LLMFactory.create(provider, model)
        self.graph_builder = EnhancedGraphBuilder(model=self.llm, embedding_model=embedding_model)

    def run(self, usecase: str, message: str) -> Dict[str, Any]:
        graph = self.graph_builder.setup_graph(usecase)
        state: Dict[str, Any] = {
            "messages": [HumanMessage(content=message)],
            "usecase": usecase,
        }
        logger.info(f"chat_service {usecase}")
        return graph.invoke(state)

