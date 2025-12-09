from tavily import TavilyClient
from langchain_core.prompts import ChatPromptTemplate
from ..common.logger import logger

class AINewsNode:
    def __init__(self,llm):
        logger.info("Initializing AINewsNode")
        self.tavily = TavilyClient()
        self.llm = llm
        self.state = {}

    def fetch_news(self, state: dict) -> dict:
        logger.info("Starting news fetch process")
        msg = state.get('messages')
        if isinstance(msg, list) and len(msg) > 0:
            first = msg[0]
            if hasattr(first, 'content'):
                frequency = str(first.content).lower()
            else:
                frequency = str(first).lower()
        elif isinstance(msg, str):
            frequency = msg.lower()
        else:
            frequency = str(state.get('frequency', 'daily')).lower()
        logger.debug(f"Fetching news with frequency: {frequency}")
        self.state['frequency'] = frequency
        time_range_map = {'daily': 'd', 'weekly': 'w', 'monthly': 'm', 'year': 'y'}
        days_map = {'daily': 1, 'weekly': 7, 'monthly': 30, 'year': 366}
        logger.info(f"Querying Tavily API for {frequency} AI news")
        response = self.tavily.search(
            query="Top Artificial Intelligence (AI) technology news India and globally",
            topic="news",
            time_range=time_range_map[frequency],
            include_answer="advanced",
            max_results=20,
            days=days_map[frequency],
        )
        state['news_data'] = response.get('results', [])
        self.state['news_data'] = state['news_data']
        logger.info(f"Successfully fetched {len(state['news_data'])} news articles")
        return state
    
    def summarize_news(self, state: dict) -> dict:
        logger.info("Starting news summarization process")
        news_items = self.state['news_data']
        logger.debug(f"Summarizing {len(news_items)} news articles")
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """Summarize AI news articles into markdown format. For each item include:
            - Date in **YYYY-MM-DD** format in IST timezone
            - Concise sentences summary from latest news
            - Sort news by date wise (latest first)
            - Source URL as link
            Use format:
            ### [Date]
            - [Summary](URL)"""),
            ("user", "Articles:\n{articles}")
        ])
        articles_str = "\n\n".join([
            f"Content: {item.get('content', '')}\nURL: {item.get('url', '')}\nDate: {item.get('published_date', '')}"
            for item in news_items
        ])
        logger.info("Invoking LLM for news summarization")
        response = self.llm.invoke(prompt_template.format(articles=articles_str))
        state['summary'] = response.content
        self.state['summary'] = state['summary']
        logger.info("News summarization completed")
        return self.state
    
    def save_result(self,state):
        logger.info("Starting to save summarized results")
        frequency = self.state['frequency']
        summary = self.state['summary']
        filename = f"./AINews/{frequency}_summary.md"
        logger.debug(f"Saving summary to file: {filename}")
        with open(filename, 'w') as f:
            f.write(f"# {frequency.capitalize()} AI News Summary\n\n")
            f.write(summary)
        self.state['filename'] = filename
        logger.info(f"Successfully saved summary to {filename}")
        return self.state

