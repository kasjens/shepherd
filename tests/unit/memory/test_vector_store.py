#!/usr/bin/env python3
"""
Unit tests for VectorMemoryStore - Phase 7

Tests vector-based memory storage, embedding generation,
and semantic similarity search capabilities.
"""

import pytest
import asyncio
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from src.memory.vector_store import VectorMemoryStore
import numpy as np


class TestVectorMemoryStore:
    """Test suite for VectorMemoryStore class."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing persistence."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def vector_store(self):
        """Create ephemeral vector store for testing."""
        return VectorMemoryStore(
            collection_name="test_collection",
            persist_directory=None  # Ephemeral
        )

    @pytest.fixture
    def persistent_vector_store(self, temp_dir):
        """Create persistent vector store for testing."""
        return VectorMemoryStore(
            collection_name="test_persistent",
            persist_directory=temp_dir
        )

    def test_initialization_ephemeral(self, vector_store):
        """Test ephemeral vector store initialization."""
        assert vector_store.collection_name == "test_collection"
        assert vector_store.persist_directory is None
        assert vector_store.encoder is not None
        assert vector_store.collection is not None

    def test_initialization_persistent(self, persistent_vector_store, temp_dir):
        """Test persistent vector store initialization."""
        assert persistent_vector_store.persist_directory == temp_dir
        assert persistent_vector_store.collection is not None

    def test_embedding_generation(self, vector_store):
        """Test text embedding generation."""
        text = "This is a test document for embedding"
        embedding = vector_store._generate_embedding(text)
        
        assert isinstance(embedding, list)
        assert len(embedding) > 0
        assert all(isinstance(x, float) for x in embedding)

    def test_data_serialization(self, vector_store):
        """Test data serialization and deserialization."""
        # Test different data types
        test_cases = [
            {"key": "value", "number": 42},
            ["list", "of", "items"],
            "simple string",
            42,
            {"nested": {"data": [1, 2, 3]}}
        ]
        
        for data in test_cases:
            serialized = vector_store._serialize_data(data)
            deserialized = vector_store._deserialize_data(serialized)
            assert deserialized == data

    def test_document_id_generation(self, vector_store):
        """Test unique document ID generation."""
        key = "test_key"
        data = {"test": "data"}
        
        id1 = vector_store._generate_document_id(key, data)
        id2 = vector_store._generate_document_id(key, data)
        
        # IDs should be different due to timestamp
        assert id1 != id2
        assert key in id1
        assert key in id2

    @pytest.mark.asyncio
    async def test_store_and_retrieve(self, vector_store):
        """Test basic store and retrieve operations."""
        key = "test_entry"
        data = {"message": "Hello, vector world!", "value": 123}
        metadata = {"category": "test", "importance": 0.8}
        
        # Store data
        await vector_store.store(key, data, metadata)
        
        # Retrieve data
        retrieved = await vector_store.retrieve(key)
        assert retrieved == data

    @pytest.mark.asyncio
    async def test_store_multiple_versions(self, vector_store):
        """Test storing multiple versions of same key."""
        key = "versioned_entry"
        
        # Store multiple versions
        data1 = {"version": 1, "content": "First version"}
        data2 = {"version": 2, "content": "Second version"}
        
        await vector_store.store(key, data1)
        await vector_store.store(key, data2)
        
        # Should retrieve most recent
        retrieved = await vector_store.retrieve(key)
        assert retrieved == data2

    @pytest.mark.asyncio
    async def test_semantic_search(self, vector_store):
        """Test semantic similarity search."""
        # Store test documents
        documents = [
            ("doc1", {"content": "Machine learning and artificial intelligence"}, {"type": "ai"}),
            ("doc2", {"content": "Web development with React and JavaScript"}, {"type": "web"}),
            ("doc3", {"content": "Deep learning neural networks"}, {"type": "ai"}),
            ("doc4", {"content": "Database design and SQL queries"}, {"type": "db"})
        ]
        
        for key, data, metadata in documents:
            await vector_store.store(key, data, metadata)
        
        # Search for AI-related content
        results = await vector_store.search({
            "text": "artificial intelligence machine learning",
            "limit": 2,
            "min_similarity": 0.3
        })
        
        assert len(results) <= 2
        # Should find AI-related documents
        ai_results = [r for r in results if r["metadata"].get("type") == "ai"]
        assert len(ai_results) > 0

    @pytest.mark.asyncio
    async def test_metadata_filtering(self, vector_store):
        """Test search with metadata filters."""
        # Store documents with different metadata
        await vector_store.store("ai1", {"content": "AI content"}, {"type": "ai", "level": "basic"})
        await vector_store.store("ai2", {"content": "Advanced AI"}, {"type": "ai", "level": "advanced"})
        await vector_store.store("web1", {"content": "Web content"}, {"type": "web", "level": "basic"})
        
        # Search with metadata filter
        results = await vector_store.search({
            "type": "ai",
            "limit": 10
        })
        
        assert len(results) == 2
        for result in results:
            assert result["metadata"]["type"] == "ai"

    @pytest.mark.asyncio
    async def test_similarity_search(self, vector_store):
        """Test find_similar method."""
        # Store reference document
        await vector_store.store("ref", {"content": "Python programming tutorial"})
        
        # Store similar and dissimilar documents
        await vector_store.store("similar", {"content": "Python coding guide"})
        await vector_store.store("different", {"content": "Cooking recipes"})
        
        # Find similar documents
        similar = await vector_store.find_similar("Python programming", limit=5, min_similarity=0.3)
        
        assert len(similar) >= 1
        # Should contain documents about Python
        python_docs = [s for s in similar if "python" in s["data"].get("content", "").lower()]
        assert len(python_docs) > 0

    @pytest.mark.asyncio
    async def test_delete_operation(self, vector_store):
        """Test delete operation."""
        key = "to_delete"
        data = {"content": "This will be deleted"}
        
        # Store and verify
        await vector_store.store(key, data)
        assert await vector_store.retrieve(key) == data
        
        # Delete and verify
        deleted = await vector_store.delete(key)
        assert deleted is True
        assert await vector_store.retrieve(key) is None
        
        # Try deleting non-existent key
        deleted_again = await vector_store.delete(key)
        assert deleted_again is False

    @pytest.mark.asyncio
    async def test_clear_operation(self, vector_store):
        """Test clear operation."""
        # Store multiple documents
        for i in range(3):
            await vector_store.store(f"doc_{i}", {"content": f"Document {i}"})
        
        # Verify they exist
        size_before = await vector_store.get_size()
        assert size_before == 3
        
        # Clear and verify
        await vector_store.clear()
        size_after = await vector_store.get_size()
        assert size_after == 0

    @pytest.mark.asyncio
    async def test_list_keys(self, vector_store):
        """Test list_keys operation."""
        # Store documents with different key patterns
        keys = ["user_pref_1", "user_pref_2", "system_config", "temp_data"]
        for key in keys:
            await vector_store.store(key, {"content": f"Content for {key}"})
        
        # List all keys
        all_keys = await vector_store.list_keys()
        assert len(all_keys) == 4
        assert set(all_keys) == set(keys)
        
        # List with pattern
        user_keys = await vector_store.list_keys("user_*")
        assert len(user_keys) == 2
        assert all(key.startswith("user_") for key in user_keys)

    @pytest.mark.asyncio
    async def test_get_size(self, vector_store):
        """Test get_size operation."""
        # Empty store
        assert await vector_store.get_size() == 0
        
        # Add documents
        for i in range(5):
            await vector_store.store(f"doc_{i}", {"content": f"Document {i}"})
        
        assert await vector_store.get_size() == 5

    @pytest.mark.asyncio
    async def test_exists_operation(self, vector_store):
        """Test exists operation."""
        key = "test_exists"
        
        # Non-existent key
        assert await vector_store.exists(key) is False
        
        # Store and check
        await vector_store.store(key, {"content": "Exists"})
        assert await vector_store.exists(key) is True
        
        # Delete and check
        await vector_store.delete(key)
        assert await vector_store.exists(key) is False

    @pytest.mark.asyncio
    async def test_batch_operations(self, vector_store):
        """Test batch store and retrieve operations."""
        # Batch store
        entries = {
            "batch1": {"content": "First batch item"},
            "batch2": {"content": "Second batch item"},
            "batch3": {"content": "Third batch item"}
        }
        
        await vector_store.store_batch(entries)
        
        # Batch retrieve
        keys = list(entries.keys())
        retrieved = await vector_store.retrieve_batch(keys)
        
        assert len(retrieved) == 3
        for key in keys:
            assert retrieved[key] == entries[key]

    @pytest.mark.asyncio
    async def test_statistics(self, vector_store):
        """Test get_statistics operation."""
        # Store test data
        await vector_store.store("test1", {"type": "string"}, {"content_type": "dict"})
        await vector_store.store("test2", [1, 2, 3], {"content_type": "list"})
        
        stats = await vector_store.get_statistics()
        
        assert "total_entries" in stats
        assert "unique_keys" in stats
        assert "content_types" in stats
        assert "collection_name" in stats
        assert "embedding_model" in stats
        
        assert stats["total_entries"] == 2
        assert stats["unique_keys"] == 2
        assert stats["collection_name"] == "test_collection"

    @pytest.mark.asyncio
    async def test_error_handling(self, vector_store):
        """Test error handling in various operations."""
        # Test with invalid data that might cause serialization issues
        with patch.object(vector_store, '_serialize_data', side_effect=Exception("Serialization error")):
            await vector_store.store("error_test", {"data": "test"})
            # Should not raise exception, but log error
        
        # Test embedding generation failure
        with patch.object(vector_store, '_generate_embedding', side_effect=Exception("Embedding error")):
            await vector_store.store("embed_error", {"data": "test"})
            # Should fall back to zero embedding

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, vector_store):
        """Test concurrent store and retrieve operations."""
        # Concurrent stores
        store_tasks = []
        for i in range(10):
            task = vector_store.store(f"concurrent_{i}", {"value": i})
            store_tasks.append(task)
        
        await asyncio.gather(*store_tasks)
        
        # Verify all stored
        size = await vector_store.get_size()
        assert size == 10
        
        # Concurrent retrieves
        retrieve_tasks = []
        for i in range(10):
            task = vector_store.retrieve(f"concurrent_{i}")
            retrieve_tasks.append(task)
        
        results = await asyncio.gather(*retrieve_tasks)
        
        # Verify all retrieved correctly
        for i, result in enumerate(results):
            assert result == {"value": i}


@pytest.mark.asyncio
async def test_vector_store_persistence(temp_dir):
    """Test persistence across vector store instances."""
    # Create first instance and store data
    store1 = VectorMemoryStore(
        collection_name="persistence_test",
        persist_directory=temp_dir
    )
    
    await store1.store("persistent_key", {"content": "Persistent data"})
    size1 = await store1.get_size()
    assert size1 == 1
    
    # Create second instance with same persistence directory
    store2 = VectorMemoryStore(
        collection_name="persistence_test",
        persist_directory=temp_dir
    )
    
    # Should load existing data
    retrieved = await store2.retrieve("persistent_key")
    assert retrieved == {"content": "Persistent data"}
    
    size2 = await store2.get_size()
    assert size2 == 1


if __name__ == "__main__":
    pytest.main([__file__])