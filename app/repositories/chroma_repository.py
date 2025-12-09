from typing import List, Dict, Any, Optional
from backend.app.database.chroma_manager import ChromaManager

class ChromaRepository:
    def __init__(self, collection_name: str = "qa_collection", embedding_model: str = "nomic-embed-text"):
        self.manager = ChromaManager(collection_name=collection_name, embedding_model=embedding_model)

    def search(self, query: str, usecase: str, limit: int = 5, score_threshold: float = 0.8) -> List[Dict[str, Any]]:
        """Search for similar questions"""
        return self.manager.search_similar_questions(
            query=query, 
            usecase=usecase, 
            limit=limit, 
            score_threshold=score_threshold
        )

    def store(self, question: str, answer: str, usecase: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Store a question-answer pair"""
        return self.manager.store_qa_pair(
            question=question, 
            answer=answer, 
            usecase=usecase, 
            metadata=metadata or {}
        )

    def stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        return self.manager.get_collection_stats()

    def clear(self) -> bool:
        """Clear the collection"""
        return self.manager.clear_collection()