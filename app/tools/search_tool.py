from langchain_tavily import TavilySearch
from langgraph.prebuilt import ToolNode
from ..common.logger import logger

def get_tools():
    try:
        logger.info("Initializing Tavily search tool")
        tavily_tool = TavilySearch(max_results=5, include_answer=True)
        logger.info("Tavily search tool initialized successfully")
        return [tavily_tool]
    except Exception as e:
        logger.critical(f"Failed to initialize Tavily search tool: {str(e)}")
        raise

def create_tool_node(tools):
    try:
        logger.info("Creating tool node for graph")
        tool_node = ToolNode(tools=tools)
        logger.info("Tool node created successfully")
        return tool_node
    except Exception as e:
        logger.critical(f"Failed to create tool node: {str(e)}")
        raise

