"""
Vector-based memory store for semantic similarity search.

This module implements vector embeddings and similarity search for the Shepherd
memory system, enabling semantic retrieval of stored memories and patterns.
"""

import asyncio
import hashlib
import json
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging

import numpy as np
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

from .base import BaseMemory

logger = logging.getLogger(__name__)


class VectorMemoryStore(BaseMemory):
    """
    Vector-based memory store using ChromaDB for semantic similarity search.
    
    This implementation uses sentence transformers to generate embeddings
    and ChromaDB for efficient vector storage and retrieval.
    """
    
    def __init__(self, collection_name: str = "shepherd_memories", 
                 embedding_model: str = "all-MiniLM-L6-v2",
                 persist_directory: Optional[str] = None):
        """
        Initialize the vector memory store.
        
        Args:
            collection_name: Name for the ChromaDB collection
            embedding_model: Sentence transformer model to use for embeddings
            persist_directory: Optional directory to persist the database
        """
        self.collection_name = collection_name
        self.embedding_model_name = embedding_model
        self.persist_directory = persist_directory
        
        # Initialize ChromaDB client
        if persist_directory:
            self.client = chromadb.PersistentClient(
                path=persist_directory,
                settings=Settings(anonymized_telemetry=False)
            )
        else:
            self.client = chromadb.EphemeralClient(
                settings=Settings(anonymized_telemetry=False)
            )
        
        # Initialize sentence transformer
        try:
            self.encoder = SentenceTransformer(embedding_model)
        except Exception as e:
            logger.error(f"Failed to load embedding model {embedding_model}: {e}")
            # Fallback to a basic model
            self.encoder = SentenceTransformer("all-MiniLM-L6-v2")
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(collection_name)
            logger.info(f"Loaded existing collection: {collection_name}")
        except Exception:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": "Shepherd vector memory store"}
            )
            logger.info(f"Created new collection: {collection_name}")
    
    def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text using sentence transformer.
        
        Args:
            text: Text to encode
            
        Returns:
            List of floats representing the embedding
        """
        try:
            embedding = self.encoder.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Failed to generate embedding for text: {e}")
            # Return zero embedding as fallback
            return [0.0] * self.encoder.get_sentence_embedding_dimension()
    
    def _serialize_data(self, data: Any) -> str:
        """
        Serialize data to string for storage.
        
        Args:
            data: Data to serialize
            
        Returns:
            JSON string representation
        """
        try:
            return json.dumps(data, default=str, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to serialize data: {e}")
            return str(data)
    
    def _deserialize_data(self, data_str: str) -> Any:
        """
        Deserialize data from string.
        
        Args:
            data_str: JSON string to deserialize
            
        Returns:
            Deserialized data
        """
        try:
            return json.loads(data_str)
        except Exception:
            # Return as string if JSON parsing fails
            return data_str
    
    def _generate_document_id(self, key: str, data: Any) -> str:
        """
        Generate a unique document ID based on key and content.
        
        Args:
            key: Storage key
            data: Data being stored
            
        Returns:
            Unique document ID
        """
        content_hash = hashlib.md5(
            self._serialize_data(data).encode('utf-8')
        ).hexdigest()[:8]
        timestamp = str(int(time.time()))
        return f"{key}_{timestamp}_{content_hash}"
    
    async def store(self, key: str, data: Any, metadata: Optional[Dict] = None) -> None:
        """
        Store data with vector embedding for semantic search.
        
        Args:
            key: Unique identifier for the stored data
            data: The data to store
            metadata: Optional metadata about the stored data
        """
        try:
            # Serialize data for text embedding
            text_content = self._serialize_data(data)
            
            # Generate embedding
            embedding = self._generate_embedding(text_content)
            
            # Prepare metadata
            storage_metadata = {
                "key": key,
                "timestamp": datetime.now().isoformat(),
                "content_type": type(data).__name__,
                "content_length": len(text_content),
                **(metadata or {})
            }
            
            # Generate unique document ID
            doc_id = self._generate_document_id(key, data)
            
            # Store in ChromaDB
            self.collection.add(
                embeddings=[embedding],
                documents=[text_content],
                metadatas=[storage_metadata],
                ids=[doc_id]
            )
            
            logger.debug(f"Stored vector memory entry: {key} -> {doc_id}")
            
        except Exception as e:
            logger.error(f"Failed to store vector memory entry {key}: {e}")
            raise
    
    async def retrieve(self, key: str) -> Optional[Any]:
        """
        Retrieve the most recent data for a key.
        
        Args:
            key: The key to look up
            
        Returns:
            The most recent stored data if found, None otherwise
        """
        try:
            # Query by metadata key
            results = self.collection.get(
                where={"key": key},
                include=["documents", "metadatas"]
            )
            
            if not results["documents"]:
                return None
            
            # Find most recent entry
            entries = list(zip(results["documents"], results["metadatas"]))
            most_recent = max(entries, 
                            key=lambda x: x[1].get("timestamp", ""))
            
            return self._deserialize_data(most_recent[0])
            
        except Exception as e:
            logger.error(f"Failed to retrieve vector memory entry {key}: {e}")
            return None
    
    async def search(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search memory using both semantic similarity and metadata filters.
        
        Args:
            query: Search criteria, can include:
                  - "text": Text for semantic similarity search
                  - "limit": Maximum number of results (default: 10)
                  - "min_similarity": Minimum similarity score (default: 0.0)
                  - Any metadata fields for filtering
        
        Returns:
            List of matching memory entries with similarity scores
        """
        try:
            text_query = query.get("text", "")
            limit = query.get("limit", 10)
            min_similarity = query.get("min_similarity", 0.0)
            
            # Prepare metadata filters (exclude special query params)
            metadata_filters = {
                k: v for k, v in query.items() 
                if k not in ["text", "limit", "min_similarity"]
            }
            
            if text_query:
                # Semantic similarity search
                query_embedding = self._generate_embedding(text_query)
                
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=limit * 2,  # Get more to filter
                    where=metadata_filters if metadata_filters else None,
                    include=["documents", "metadatas", "distances"]
                )
                
                # Process results with similarity filtering
                matches = []
                if results["documents"] and results["documents"][0]:
                    for doc, meta, distance in zip(
                        results["documents"][0],
                        results["metadatas"][0], 
                        results["distances"][0]
                    ):
                        # Convert distance to similarity (ChromaDB uses distance)
                        similarity = 1.0 - distance
                        
                        if similarity >= min_similarity:
                            matches.append({
                                "data": self._deserialize_data(doc),
                                "metadata": meta,
                                "similarity": similarity,
                                "key": meta.get("key", "unknown")
                            })
                
                # Sort by similarity and limit results
                matches.sort(key=lambda x: x["similarity"], reverse=True)
                return matches[:limit]
            
            else:
                # Metadata-only search
                results = self.collection.get(
                    where=metadata_filters if metadata_filters else None,
                    limit=limit,
                    include=["documents", "metadatas"]
                )
                
                matches = []
                if results["documents"]:
                    for doc, meta in zip(results["documents"], results["metadatas"]):
                        matches.append({
                            "data": self._deserialize_data(doc),
                            "metadata": meta,
                            "similarity": 1.0,  # No similarity for metadata-only
                            "key": meta.get("key", "unknown")
                        })
                
                return matches
                
        except Exception as e:
            logger.error(f"Failed to search vector memory: {e}")
            return []
    
    async def delete(self, key: str) -> bool:
        """
        Delete all entries for a key.
        
        Args:
            key: The key to delete
            
        Returns:
            True if any entries were deleted, False otherwise
        """
        try:
            # Get all entries for the key
            results = self.collection.get(
                where={"key": key},
                include=["metadatas"]
            )
            
            if not results["ids"]:
                return False
            
            # Delete all entries
            self.collection.delete(ids=results["ids"])
            
            logger.debug(f"Deleted {len(results['ids'])} vector memory entries for key: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete vector memory entries for {key}: {e}")
            return False
    
    async def clear(self) -> None:
        """
        Clear all entries from the vector store.
        """
        try:
            # Delete the collection and recreate it
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Shepherd vector memory store"}
            )
            logger.info(f"Cleared vector memory collection: {self.collection_name}")
            
        except Exception as e:
            logger.error(f"Failed to clear vector memory: {e}")
            raise
    
    async def list_keys(self, pattern: Optional[str] = None) -> List[str]:
        """
        List all unique keys in the vector store.
        
        Args:
            pattern: Optional pattern to filter keys (simple wildcard support)
            
        Returns:
            List of unique keys
        """
        try:
            # Get all metadata
            results = self.collection.get(include=["metadatas"])
            
            if not results["metadatas"]:
                return []
            
            # Extract unique keys
            keys = set()
            for meta in results["metadatas"]:
                key = meta.get("key")
                if key:
                    if pattern:
                        # Simple wildcard matching
                        if pattern.endswith("*"):
                            if key.startswith(pattern[:-1]):
                                keys.add(key)
                        elif pattern.startswith("*"):
                            if key.endswith(pattern[1:]):
                                keys.add(key)
                        elif pattern in key:
                            keys.add(key)
                    else:
                        keys.add(key)
            
            return sorted(list(keys))
            
        except Exception as e:
            logger.error(f"Failed to list vector memory keys: {e}")
            return []
    
    async def get_size(self) -> int:
        """
        Get the number of entries in the vector store.
        
        Returns:
            Number of stored entries
        """
        try:
            results = self.collection.get(include=["metadatas"])
            return len(results["metadatas"]) if results["metadatas"] else 0
            
        except Exception as e:
            logger.error(f"Failed to get vector memory size: {e}")
            return 0
    
    async def find_similar(self, content: str, limit: int = 5, 
                          min_similarity: float = 0.5) -> List[Dict[str, Any]]:
        """
        Find entries similar to the given content.
        
        Args:
            content: Text content to find similarities for
            limit: Maximum number of results
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of similar entries with similarity scores
        """
        return await self.search({
            "text": content,
            "limit": limit,
            "min_similarity": min_similarity
        })
    
    async def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the vector memory store.
        
        Returns:
            Dictionary with statistics
        """
        try:
            size = await self.get_size()
            keys = await self.list_keys()
            
            # Get metadata for analysis
            results = self.collection.get(include=["metadatas"])
            
            content_types = {}
            timestamps = []
            
            if results["metadatas"]:
                for meta in results["metadatas"]:
                    # Count content types
                    content_type = meta.get("content_type", "unknown")
                    content_types[content_type] = content_types.get(content_type, 0) + 1
                    
                    # Collect timestamps
                    timestamp = meta.get("timestamp")
                    if timestamp:
                        timestamps.append(timestamp)
            
            return {
                "total_entries": size,
                "unique_keys": len(keys),
                "content_types": content_types,
                "collection_name": self.collection_name,
                "embedding_model": self.embedding_model_name,
                "oldest_entry": min(timestamps) if timestamps else None,
                "newest_entry": max(timestamps) if timestamps else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get vector memory statistics: {e}")
            return {"error": str(e)}