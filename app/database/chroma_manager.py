import os
import hashlib
from typing import List, Dict, Optional, Any
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from ..common.logger import logger
import numpy as np

class ChromaManager:
    def __init__(self, collection_name: str = "qa_collection", embedding_model: str = "nomic-embed-text"):
        host_addr = os.getenv("CHROMA_HOST_ADDR", "").strip()
        host_port = int(os.getenv("CHROMA_HOST_PORT", "8000"))
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
        
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        self._ensure_collection_exists()

    def _ensure_collection_exists(self):
        """Ensure the collection exists, create if it doesn't"""
        try:
            # Try to get existing collection
            self.collection = self.client.get_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function
            )
            logger.info(f"Using existing collection: {self.collection_name}")
        except Exception as e:
            logger.info(f"Creating new collection: {self.collection_name}")
            try:
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    embedding_function=self.embedding_function,
                    metadata={"hnsw:space": "cosine"}  # Use cosine similarity
                )
            except Exception as create_error:
                logger.error(f"Error creating collection: {create_error}")
                raise

    def _generate_id(self, text: str) -> str:
        """Generate a unique ID for a document"""
        return hashlib.md5(text.encode()).hexdigest()

    def store_qa_pair(self, question: str, answer: str, usecase: str, metadata: Optional[Dict] = None) -> bool:
        """Store a question-answer pair in ChromaDB"""
        try:
            # Generate unique ID
            doc_id = self._generate_id(f"{question}_{usecase}")
            
            # Prepare metadata
            chroma_metadata = {
                "question": question,
                "answer": answer,
                "usecase": usecase,
                "timestamp": np.datetime64('now').astype('datetime64[s]').item().isoformat(),
                **(metadata or {})
            }
            
            # Store in ChromaDB
            self.collection.add(
                documents=[question],
                metadatas=[chroma_metadata],
                ids=[doc_id]
            )
            
            logger.info(f"Stored Q&A pair with ID: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing Q&A pair: {e}")
            return False

    def search_similar_questions(self, query: str, usecase: str, limit: int = 5, score_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Search for similar questions in ChromaDB"""
        try:
            # Query ChromaDB with usecase filter
            results = self.collection.query(
                query_texts=[query],
                n_results=min(limit, 10),  # ChromaDB limit
                where={"usecase": usecase},
                include=["documents", "metadatas", "distances"]
            )
            
            # Process results
            similar_questions = []
            
            if results['ids'] and results['ids'][0]:
                for i, doc_id in enumerate(results['ids'][0]):
                    distance = results['distances'][0][i]
                    # Convert distance to similarity score (ChromaDB uses L2 distance by default)
                    # For cosine similarity, lower distance = higher similarity
                    similarity_score = 1 - distance if distance <= 1 else 0
                    
                    if similarity_score >= score_threshold:
                        metadata = results['metadatas'][0][i]
                        similar_questions.append({
                            "question": metadata.get("question", ""),
                            "answer": metadata.get("answer", ""),
                            "score": similarity_score,
                            "metadata": {k: v for k, v in metadata.items() if k not in ["question", "answer"]}
                        })
            
            # Sort by score (highest first)
            similar_questions.sort(key=lambda x: x["score"], reverse=True)
            
            logger.info(f"Found {len(similar_questions)} similar questions for query: {query}")
            return similar_questions
            
        except Exception as e:
            logger.error(f"Error searching similar questions: {e}")
            return []

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        try:
            count = self.collection.count()
            return {
                "collection_name": self.collection_name,
                "total_documents": count,
                "embedding_model": self.embedding_model
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {"error": str(e)}

    def clear_collection(self) -> bool:
        """Clear all documents from the collection"""
        try:
            self.client.delete_collection(self.collection_name)
            self._ensure_collection_exists()
            logger.info(f"Cleared collection: {self.collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            return False
