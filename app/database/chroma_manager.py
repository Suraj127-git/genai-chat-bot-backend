import os
import hashlib
from typing import List, Dict, Optional, Any
import chromadb
from chromadb.config import Settings

from ..common.logger import logger
import numpy as np


class ChromaManager:
    def __init__(self, collection_name: str = "qa_collection", embedding_model: str = "nomic-embed-text"):
        host_addr = os.getenv("CHROMA_HOST_ADDR", "").strip()
        host_port = int(os.getenv("CHROMA_HOST_PORT", "8000"))
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        self._is_remote = bool(host_addr)

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

    def _switch_to_local_client(self):
        persist_directory = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        self._is_remote = False
        logger.info(f"Falling back to local ChromaDB at {persist_directory}")

    def _ensure_collection_exists(self, allow_fallback: bool = True):
        """Ensure the collection exists, create if it doesn't"""
        try:
            try:
                collections = self.client.list_collections()
                for coll in collections:
                    if getattr(coll, "name", None) == self.collection_name:
                        self.collection = coll
                        logger.info(f"Using existing collection from list_collections: {self.collection_name}")
                        return
            except Exception as list_error:
                logger.warning(f"Could not list collections: {list_error}")

            try:
                self.collection = self.client.get_collection(name=self.collection_name)
                logger.info(f"Using existing collection via get_collection: {self.collection_name}")
                return
            except Exception as get_error:
                logger.info(f"Collection {self.collection_name} not found via get_collection, will create: {get_error}")

            try:
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"hnsw:space": "cosine"}
                )
                logger.info(f"Created new collection with metadata: {self.collection_name}")
            except Exception as create_error:
                msg = str(create_error)
                logger.warning(f"Standard create_collection failed: {msg}")
                if "already exists" in msg:
                    self.collection = self.client.get_collection(name=self.collection_name)
                    logger.info(f"Collection already exists, fetched via get_collection: {self.collection_name}")
                else:
                    try:
                        self.collection = self.client.create_collection(name=self.collection_name)
                        logger.info(f"Created collection with minimal metadata: {self.collection_name}")
                    except Exception as minimal_error:
                        logger.error(f"All collection creation attempts failed: {minimal_error}")
                        raise minimal_error

            logger.info(f"Ensured collection exists: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error ensuring collection exists: {e}")
            if allow_fallback and self._is_remote and "_type" in str(e):
                logger.warning("Remote ChromaDB error related to configuration type; falling back to local persistent ChromaDB")
                self._switch_to_local_client()
                self._ensure_collection_exists(allow_fallback=False)
            else:
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
