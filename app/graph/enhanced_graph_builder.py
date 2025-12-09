from langgraph.graph import StateGraph
from langgraph.graph import START, END
from ..state.state import State
from ..nodes.enhanced_chatbot_node import EnhancedChatbotNode
from ..nodes.enhanced_ai_news_node import EnhancedAINewsNode
from ..tools.search_tool import get_tools, create_tool_node
from langgraph.prebuilt import tools_condition
from ..nodes.chatbot_with_Tool_node import ChatbotWithToolNode
from ..common.logger import logger
from ..repositories.chroma_repository import ChromaRepository
import traceback

class EnhancedGraphBuilder:
    def __init__(self, model, embedding_model: str = "nomic-embed-text"):
        self.llm = model
        self.embedding_model = embedding_model
        self.graph_builder = StateGraph(State)
        self.chroma_repo = ChromaRepository(embedding_model=embedding_model)

    def enhanced_basic_chatbot_build_graph(self):
        logger.info("Building enhanced basic chatbot graph")
        enhanced_chatbot_node = EnhancedChatbotNode(model=self.llm, embedding_model=self.embedding_model)
        self.graph_builder.add_node("chatbot", enhanced_chatbot_node.process)
        self.graph_builder.add_edge(START, "chatbot")
        self.graph_builder.add_edge("chatbot", END)

    def enhanced_ai_news_builder_graph(self):
        logger.info("Building enhanced AI news graph")
        enhanced_ai_news_node = EnhancedAINewsNode(model=self.llm, embedding_model=self.embedding_model)
        self.graph_builder.add_node("fetch_news", enhanced_ai_news_node.fetch_news)
        self.graph_builder.add_node("summarize_news", enhanced_ai_news_node.summarize_news)
        self.graph_builder.add_node("save_result", enhanced_ai_news_node.save_result)
        self.graph_builder.set_entry_point("fetch_news")
        self.graph_builder.add_edge("fetch_news", "summarize_news")
        self.graph_builder.add_edge("summarize_news", "save_result")
        self.graph_builder.add_edge("save_result", END)

    def chatbot_with_tools_build_graph(self):
        logger.info("Building chatbot with tools graph")
        tools = get_tools()
        tool_node = create_tool_node(tools)
        obj_chatbot_with_node = ChatbotWithToolNode(self.llm)
        chatbot_node = obj_chatbot_with_node.create_chatbot(tools)
        self.graph_builder.add_node("chatbot", chatbot_node)
        self.graph_builder.add_node("tools", tool_node)
        self.graph_builder.add_edge(START, "chatbot")
        self.graph_builder.add_conditional_edges("chatbot", tools_condition)
        self.graph_builder.add_edge("tools", "chatbot")

    def setup_graph(self, usecase: str):
        try:
            logger.info(f"Setting up enhanced graph for use case: {usecase}")
            if usecase == "Basic Chatbot":
                self.enhanced_basic_chatbot_build_graph()
            elif usecase == "Chatbot With Web":
                self.chatbot_with_tools_build_graph()
            elif usecase == "AI News":
                self.enhanced_ai_news_builder_graph()
            else:
                logger.error(f"Invalid use case selected: {usecase}")
                raise ValueError(f"Invalid use case: {usecase}")
            logger.info("Enhanced graph setup completed successfully")
            return self.graph_builder.compile()
        except Exception as e:
            tb = traceback.format_exc()
            logger.critical(f"Failed to setup enhanced graph for {usecase}: {e}\n{tb}")
            raise

    def get_database_stats(self):
        return self.chroma_repo.stats()

    def clear_database(self):
        return self.chroma_repo.clear()

