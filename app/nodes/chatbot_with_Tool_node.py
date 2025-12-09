from langgraph.prebuilt import ToolNode
from backend.app.common.logger import logger

class ChatbotWithToolNode:
    def __init__(self, llm):
        self.llm = llm

    def create_chatbot(self, tools):
        logger.info("Creating chatbot with tool node")
        return ToolNode(tools=tools)

