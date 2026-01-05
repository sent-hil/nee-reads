"""Tests for database module."""

import pytest
from pathlib import Path

from api.database import (
    init_database,
    get_db_connection,
    clear_expired_cache,
)


class TestInitDatabase:
    """Tests for init_database function."""

    async def test_creates_search_cache_table(self, temp_db_path: Path) -> None:
        """Test that init_database creates the search_cache table."""
        await init_database(temp_db_path)

        async with get_db_connection(temp_db_path) as db:
            cursor = await db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='search_cache'"
            )
            result = await cursor.fetchone()
            assert result is not None
            assert result[0] == "search_cache"

    async def test_creates_query_hash_index(self, temp_db_path: Path) -> None:
        """Test that init_database creates the query_hash index."""
        await init_database(temp_db_path)

        async with get_db_connection(temp_db_path) as db:
            cursor = await db.execute(
                "SELECT name FROM sqlite_master WHERE type='index' AND name='idx_query_hash'"
            )
            result = await cursor.fetchone()
            assert result is not None

    async def test_creates_expires_at_index(self, temp_db_path: Path) -> None:
        """Test that init_database creates the expires_at index."""
        await init_database(temp_db_path)

        async with get_db_connection(temp_db_path) as db:
            cursor = await db.execute(
                "SELECT name FROM sqlite_master WHERE type='index' AND name='idx_expires_at'"
            )
            result = await cursor.fetchone()
            assert result is not None

    async def test_idempotent_initialization(self, temp_db_path: Path) -> None:
        """Test that init_database can be called multiple times without error."""
        await init_database(temp_db_path)
        await init_database(temp_db_path)  # Should not raise

        async with get_db_connection(temp_db_path) as db:
            cursor = await db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='search_cache'"
            )
            result = await cursor.fetchone()
            assert result is not None


class TestGetDbConnection:
    """Tests for get_db_connection function."""

    async def test_returns_connection(self, temp_db_path: Path) -> None:
        """Test that get_db_connection returns a valid connection."""
        await init_database(temp_db_path)
        async with get_db_connection(temp_db_path) as db:
            assert db is not None
            cursor = await db.execute("SELECT 1")
            result = await cursor.fetchone()
            assert result[0] == 1


class TestClearExpiredCache:
    """Tests for clear_expired_cache function."""

    async def test_removes_expired_entries(self, initialized_db: Path) -> None:
        """Test that expired entries are removed."""
        async with get_db_connection(initialized_db) as db:
            # Insert an expired entry
            await db.execute(
                """
                INSERT INTO search_cache 
                (query_hash, query, page, limit_val, response_json, expires_at)
                VALUES (?, ?, ?, ?, ?, datetime('now', '-1 hour'))
                """,
                ("hash1", "test", 1, 100, "{}"),
            )
            # Insert a valid entry
            await db.execute(
                """
                INSERT INTO search_cache 
                (query_hash, query, page, limit_val, response_json, expires_at)
                VALUES (?, ?, ?, ?, ?, datetime('now', '+1 hour'))
                """,
                ("hash2", "test2", 1, 100, "{}"),
            )
            await db.commit()

        deleted = await clear_expired_cache(initialized_db)
        assert deleted == 1

        async with get_db_connection(initialized_db) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM search_cache")
            result = await cursor.fetchone()
            assert result[0] == 1

    async def test_returns_zero_when_no_expired(self, initialized_db: Path) -> None:
        """Test that zero is returned when no expired entries exist."""
        deleted = await clear_expired_cache(initialized_db)
        assert deleted == 0
