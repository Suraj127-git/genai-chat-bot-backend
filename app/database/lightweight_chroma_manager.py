import os
import hashlib
from typing import List, Dict, Optional, Any
import chromadb
from chromadb.config import Settings

from ..common.logger import logger


class LightweightChromaManager:
    def __init__(self, collection_name: str = "qa_collection", embedding_model: str = "nomic-embed-text"):
        host_addr = os.getenv("CHROMA_HOST_ADDR", "").strip()
        host_port = int(os.getenv("CHROMA_HOST_PORT", "8000"))
        self.collection_name = collection_name

        if host_addr:
            self.client = chromadb.HttpClient(host=host_addr, port=host_port, ssl=False)
            logger.info(f"Connected to remote ChromaDB at {host_addr}:{host_port}")
        else:
            persist_directory = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")
            self.client = chromadb.PersistentClient(
                path=persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            logger.info(f"Using local ChromaDB at {persist_directory}")

        self._ensure_collection_exists()

    def _ensure_collection_exists(self):
        """Ensure the collection exists, create if it doesn't"""
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
            logger.info(f"Using existing collection: {self.collection_name}")
        except Exception:
            logger.info(f"Creating new collection: {self.collection_name}")
            self.collection = self.client.create_collection(name=self.collection_name)

    def store_qa_pair(self, question: str, answer: str, usecase: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Store a question-answer pair with metadata"""
        try:
            # Generate unique ID for the document
            doc_id = hashlib.md5(f"{question}_{usecase}".encode()).hexdigest()
            
            # Prepare metadata
            doc_metadata = {
                "usecase": usecase,
                "question": question,
                "answer": answer
            }
            if metadata:
                doc_metadata.update(metadata)
            
            # Store in ChromaDB
            self.collection.add(
                documents=[question],
                metadatas=[doc_metadata],
                ids=[doc_id]
            )
            logger.info(f"Stored QA pair for usecase: {usecase}")
            return True
        except Exception as e:
            logger.error(f"Failed to store QA pair: {str(e)}")
            return False

    def search_similar_questions(self, query: str, usecase: str, limit: int = 5, score_threshold: float = 0.8) -> List[Dict[str, Any]]:
        """Search for similar questions and return relevant answers"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=min(limit, 10),
                where={"usecase": usecase}
            )
            
            if not results['documents'] or not results['documents'][0]:
                return []
            
            # Format results
            formatted_results = []
            for i, doc in enumerate(results['documents'][0]):
                metadata = results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {}
                distance = results['distances'][0][i] if results['distances'] and results['distances'][0] else 0
                
                # Convert distance to similarity score (lower distance = higher similarity)
                similarity_score = max(0, 1 - distance)
                
                if similarity_score >= score_threshold:
                    formatted_results.append({
                        "question": doc,
                        "answer": metadata.get("answer", ""),
                        "similarity_score": similarity_score,
                        "metadata": metadata
                    })
            
            # Sort by similarity score
            formatted_results.sort(key=lambda x: x["similarity_score"], reverse=True)
            
            logger.info(f"Found {len(formatted_results)} similar questions for usecase: {usecase}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to search similar questions: {str(e)}")
            return []

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        try:
            count = self.collection.count()
            return {
                "collection_name": self.collection_name,
                "total_documents": count,
                "embedding_model": "default",
                "status": "active"
            }
        except Exception as e:
            logger.error(f"Failed to get collection stats: {str(e)}")
            return {
                "collection_name": self.collection_name,
                "total_documents": 0,
                "embedding_model": "default",
                "status": "error",
                "error": str(e)
            }

    def clear_collection(self) -> bool:
        """Clear all documents from the collection"""
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(name=self.collection_name)
            logger.info(f"Cleared collection: {self.collection_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to clear collection: {str(e)}")
            return False
