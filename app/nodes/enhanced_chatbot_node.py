from typing import Dict, Any
from ..state.state import State
from ..common.logger import logger
from ..repositories.chroma_repository import ChromaRepository

class EnhancedChatbotNode:
    def __init__(self, model, embedding_model: str = "nomic-embed-text"):
        self.llm = model
        self.chroma_repo = ChromaRepository(embedding_model=embedding_model)
        self.similarity_threshold = 0.8

    def process(self, state: State) -> Dict[str, Any]:
        logger.info(f"EnhancedChatbotNode processing state: {state}")
        messages = state.get('messages', [])
        if not messages:
            logger.warning("No messages found in state")
            return {"messages": []}
        user_question = messages[-1].content if hasattr(messages[-1], 'content') else str(messages[-1])
        usecase = state.get('usecase', 'Basic Chatbot')
        similar_questions = self.chroma_repo.search(query=user_question, usecase=usecase, limit=3, score_threshold=self.similarity_threshold)
        if similar_questions and similar_questions[0]['score'] > self.similarity_threshold:
            logger.info(f"Found similar question with score: {similar_questions[0]['score']}")
            cached_answer = similar_questions[0]['answer']
            enhanced_answer = f"{cached_answer}\n\n*[This response was retrieved from previous similar questions]*"
            return {"messages": [enhanced_answer]}
        logger.info("No similar questions found, generating new response")
        response = self.llm.invoke(state['messages'])
        if hasattr(response, 'content'):
            answer_content = response.content
        else:
            answer_content = str(response)
        self.chroma_repo.store(question=user_question, answer=answer_content, usecase=usecase, metadata={"model": str(self.llm), "method": "llm_generated"})
        return {"messages": response}

