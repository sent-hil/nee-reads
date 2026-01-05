"""Tests for cache service."""

import pytest
from pathlib import Path

from api.services.cache import (
    generate_cache_key,
    get_cached_response,
    store_cached_response,
    invalidate_cache,
    clear_all_cache,
)
from api.database import get_db_connection


class TestGenerateCacheKey:
    """Tests for generate_cache_key function."""

    def test_generates_consistent_hash(self) -> None:
        """Test that same inputs produce same hash."""
        key1 = generate_cache_key("test query", 1, 100)
        key2 = generate_cache_key("test query", 1, 100)
        assert key1 == key2

    def test_normalizes_query_case(self) -> None:
        """Test that query is case-insensitive."""
        key1 = generate_cache_key("Test Query", 1, 100)
        key2 = generate_cache_key("test query", 1, 100)
        assert key1 == key2

    def test_normalizes_query_whitespace(self) -> None:
        """Test that leading/trailing whitespace is stripped."""
        key1 = generate_cache_key("  test query  ", 1, 100)
        key2 = generate_cache_key("test query", 1, 100)
        assert key1 == key2

    def test_different_pages_produce_different_keys(self) -> None:
        """Test that different pages produce different hashes."""
        key1 = generate_cache_key("test", 1, 100)
        key2 = generate_cache_key("test", 2, 100)
        assert key1 != key2

    def test_different_limits_produce_different_keys(self) -> None:
        """Test that different limits produce different hashes."""
        key1 = generate_cache_key("test", 1, 50)
        key2 = generate_cache_key("test", 1, 100)
        assert key1 != key2

    def test_returns_sha256_hex_string(self) -> None:
        """Test that the key is a valid SHA256 hex string."""
        key = generate_cache_key("test", 1, 100)
        assert len(key) == 64  # SHA256 produces 64 hex characters
        assert all(c in "0123456789abcdef" for c in key)


class TestStoreCachedResponse:
    """Tests for store_cached_response function."""

    async def test_stores_response(self, initialized_db: Path) -> None:
        """Test that a response is stored in the cache."""
        response = {"numFound": 1, "docs": [{"title": "Test Book"}]}
        await store_cached_response("test query", 1, 100, response, initialized_db)

        async with get_db_connection(initialized_db) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM search_cache")
            result = await cursor.fetchone()
            assert result[0] == 1

    async def test_stores_with_correct_values(self, initialized_db: Path) -> None:
        """Test that stored values are correct."""
        response = {"numFound": 5, "docs": []}
        await store_cached_response("my query", 2, 50, response, initialized_db)

        async with get_db_connection(initialized_db) as db:
            cursor = await db.execute("SELECT query, page, limit_val FROM search_cache")
            result = await cursor.fetchone()
            assert result[0] == "my query"
            assert result[1] == 2
            assert result[2] == 50

    async def test_replaces_existing_entry(self, initialized_db: Path) -> None:
        """Test that storing with same key replaces existing entry."""
        response1 = {"numFound": 1, "docs": []}
        response2 = {"numFound": 2, "docs": []}

        await store_cached_response("test", 1, 100, response1, initialized_db)
        await store_cached_response("test", 1, 100, response2, initialized_db)

        async with get_db_connection(initialized_db) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM search_cache")
            result = await cursor.fetchone()
            assert result[0] == 1


class TestGetCachedResponse:
    """Tests for get_cached_response function."""

    async def test_returns_cached_response(self, initialized_db: Path) -> None:
        """Test that cached response is returned."""
        response = {"numFound": 3, "docs": [{"title": "Cached Book"}]}
        await store_cached_response("test", 1, 100, response, initialized_db)

        result = await get_cached_response("test", 1, 100, initialized_db)
        assert result == response

    async def test_returns_none_for_miss(self, initialized_db: Path) -> None:
        """Test that None is returned for cache miss."""
        result = await get_cached_response("nonexistent", 1, 100, initialized_db)
        assert result is None

    async def test_returns_none_for_expired(self, initialized_db: Path) -> None:
        """Test that None is returned for expired entries."""
        async with get_db_connection(initialized_db) as db:
            query_hash = generate_cache_key("expired", 1, 100)
            await db.execute(
                """
                INSERT INTO search_cache 
                (query_hash, query, page, limit_val, response_json, expires_at)
                VALUES (?, ?, ?, ?, ?, datetime('now', '-1 hour'))
                """,
                (query_hash, "expired", 1, 100, '{"numFound": 0, "docs": []}'),
            )
            await db.commit()

        result = await get_cached_response("expired", 1, 100, initialized_db)
        assert result is None

    async def test_case_insensitive_query(self, initialized_db: Path) -> None:
        """Test that query matching is case-insensitive."""
        response = {"numFound": 1, "docs": []}
        await store_cached_response("Test Query", 1, 100, response, initialized_db)

        result = await get_cached_response("test query", 1, 100, initialized_db)
        assert result == response


class TestInvalidateCache:
    """Tests for invalidate_cache function."""

    async def test_removes_specific_entry(self, initialized_db: Path) -> None:
        """Test that specific entry is removed."""
        await store_cached_response("test1", 1, 100, {}, initialized_db)
        await store_cached_response("test2", 1, 100, {}, initialized_db)

        result = await invalidate_cache("test1", 1, 100, initialized_db)
        assert result is True

        async with get_db_connection(initialized_db) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM search_cache")
            count = await cursor.fetchone()
            assert count[0] == 1

    async def test_returns_false_when_not_found(self, initialized_db: Path) -> None:
        """Test that False is returned when entry not found."""
        result = await invalidate_cache("nonexistent", 1, 100, initialized_db)
        assert result is False


class TestClearAllCache:
    """Tests for clear_all_cache function."""

    async def test_clears_all_entries(self, initialized_db: Path) -> None:
        """Test that all entries are cleared."""
        await store_cached_response("test1", 1, 100, {}, initialized_db)
        await store_cached_response("test2", 1, 100, {}, initialized_db)
        await store_cached_response("test3", 1, 100, {}, initialized_db)

        deleted = await clear_all_cache(initialized_db)
        assert deleted == 3

        async with get_db_connection(initialized_db) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM search_cache")
            count = await cursor.fetchone()
            assert count[0] == 0

    async def test_returns_zero_when_empty(self, initialized_db: Path) -> None:
        """Test that zero is returned when cache is empty."""
        deleted = await clear_all_cache(initialized_db)
        assert deleted == 0
