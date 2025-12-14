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
        logger.info(f"ChatService.run() called with usecase={usecase}, message={message}")
        graph = self.graph_builder.setup_graph(usecase)
        logger.info(f"Graph setup completed for usecase={usecase}")
        state: Dict[str, Any] = {
            "messages": [HumanMessage(content=message)],
            "usecase": usecase,
        }
        logger.info(f"Initial state created: {state}")
        try:
            result = graph.invoke(state)
            logger.info(f"Graph.invoke() completed successfully: {result}")
            return result
        except Exception as e:
            logger.error(f"Graph.invoke() failed: {e}", exc_info=True)
            raise

