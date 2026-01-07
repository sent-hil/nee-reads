"""Tests for database module."""

import pytest
from pathlib import Path

from api.database import (
    init_database,
    get_db_connection,
    clear_expired_cache,
    get_book_status,
    set_book_status,
    delete_book_status,
    get_all_book_statuses,
    get_book_statuses_batch,
    get_books_by_status,
    get_status_counts,
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

    async def test_creates_books_table(self, temp_db_path: Path) -> None:
        """Test that init_database creates the books table."""
        await init_database(temp_db_path)

        async with get_db_connection(temp_db_path) as db:
            cursor = await db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='books'"
            )
            result = await cursor.fetchone()
            assert result is not None
            assert result[0] == "books"

    async def test_creates_book_statuses_table(self, temp_db_path: Path) -> None:
        """Test that init_database creates the book_statuses table."""
        await init_database(temp_db_path)

        async with get_db_connection(temp_db_path) as db:
            cursor = await db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='book_statuses'"
            )
            result = await cursor.fetchone()
            assert result is not None
            assert result[0] == "book_statuses"

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


class TestBookStatus:
    """Tests for book status operations."""

    async def test_set_book_status_creates_book_and_status(self, initialized_db: Path) -> None:
        """Test that set_book_status creates both book and status records."""
        result = await set_book_status(
            openlibrary_work_key="/works/OL123W",
            status="to_read",
            title="Test Book",
            author_name=["Author One", "Author Two"],
            cover_url="https://example.com/cover.jpg",
            first_publish_year=2020,
            db_path=initialized_db,
        )

        assert result["openlibrary_work_key"] == "/works/OL123W"
        assert result["status"] == "to_read"
        assert result["title"] == "Test Book"
        assert result["author_name"] == ["Author One", "Author Two"]
        assert result["cover_url"] == "https://example.com/cover.jpg"
        assert result["first_publish_year"] == 2020

    async def test_set_book_status_updates_existing(self, initialized_db: Path) -> None:
        """Test that set_book_status updates an existing status."""
        await set_book_status(
            openlibrary_work_key="/works/OL123W",
            status="to_read",
            title="Test Book",
            author_name=["Author One"],
            db_path=initialized_db,
        )

        result = await set_book_status(
            openlibrary_work_key="/works/OL123W",
            status="completed",
            title="Test Book Updated",
            author_name=["Author One", "New Author"],
            db_path=initialized_db,
        )

        assert result["status"] == "completed"
        assert result["title"] == "Test Book Updated"
        assert result["author_name"] == ["Author One", "New Author"]

    async def test_get_book_status(self, initialized_db: Path) -> None:
        """Test that get_book_status retrieves a book status."""
        await set_book_status(
            openlibrary_work_key="/works/OL123W",
            status="to_read",
            title="Test Book",
            author_name=["Author One"],
            db_path=initialized_db,
        )

        result = await get_book_status("/works/OL123W", initialized_db)

        assert result is not None
        assert result["openlibrary_work_key"] == "/works/OL123W"
        assert result["status"] == "to_read"
        assert result["title"] == "Test Book"

    async def test_get_book_status_not_found(self, initialized_db: Path) -> None:
        """Test that get_book_status returns None for non-existent book."""
        result = await get_book_status("/works/NONEXISTENT", initialized_db)
        assert result is None

    async def test_delete_book_status(self, initialized_db: Path) -> None:
        """Test that delete_book_status removes both status and book."""
        await set_book_status(
            openlibrary_work_key="/works/OL123W",
            status="to_read",
            title="Test Book",
            author_name=["Author One"],
            db_path=initialized_db,
        )

        deleted = await delete_book_status("/works/OL123W", initialized_db)
        assert deleted is True

        # Verify book and status are gone
        result = await get_book_status("/works/OL123W", initialized_db)
        assert result is None

        # Verify books table is empty
        async with get_db_connection(initialized_db) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM books")
            count = await cursor.fetchone()
            assert count[0] == 0

    async def test_delete_book_status_not_found(self, initialized_db: Path) -> None:
        """Test that delete_book_status returns False for non-existent book."""
        deleted = await delete_book_status("/works/NONEXISTENT", initialized_db)
        assert deleted is False

    async def test_get_all_book_statuses(self, initialized_db: Path) -> None:
        """Test that get_all_book_statuses returns all books with statuses."""
        await set_book_status(
            openlibrary_work_key="/works/OL1W",
            status="to_read",
            title="Book One",
            author_name=["Author A"],
            db_path=initialized_db,
        )
        await set_book_status(
            openlibrary_work_key="/works/OL2W",
            status="completed",
            title="Book Two",
            author_name=["Author B"],
            db_path=initialized_db,
        )

        results = await get_all_book_statuses(initialized_db)

        assert len(results) == 2
        # Most recently updated first
        assert results[0]["openlibrary_work_key"] == "/works/OL2W"
        assert results[1]["openlibrary_work_key"] == "/works/OL1W"

    async def test_get_book_statuses_batch(self, initialized_db: Path) -> None:
        """Test that get_book_statuses_batch returns statuses for multiple books."""
        await set_book_status(
            openlibrary_work_key="/works/OL1W",
            status="to_read",
            title="Book One",
            author_name=["Author A"],
            db_path=initialized_db,
        )
        await set_book_status(
            openlibrary_work_key="/works/OL2W",
            status="completed",
            title="Book Two",
            author_name=["Author B"],
            db_path=initialized_db,
        )

        results = await get_book_statuses_batch(
            ["/works/OL1W", "/works/OL2W", "/works/OL3W"], initialized_db
        )

        assert results == {
            "/works/OL1W": "to_read",
            "/works/OL2W": "completed",
        }

    async def test_get_book_statuses_batch_empty(self, initialized_db: Path) -> None:
        """Test that get_book_statuses_batch handles empty input."""
        results = await get_book_statuses_batch([], initialized_db)
        assert results == {}

    async def test_get_books_by_status(self, initialized_db: Path) -> None:
        """Test that get_books_by_status returns books with specific status."""
        await set_book_status(
            openlibrary_work_key="/works/OL1W",
            status="to_read",
            title="Book One",
            author_name=["Author A"],
            db_path=initialized_db,
        )
        await set_book_status(
            openlibrary_work_key="/works/OL2W",
            status="completed",
            title="Book Two",
            author_name=["Author B"],
            db_path=initialized_db,
        )
        await set_book_status(
            openlibrary_work_key="/works/OL3W",
            status="to_read",
            title="Book Three",
            author_name=["Author C"],
            db_path=initialized_db,
        )

        results = await get_books_by_status("to_read", initialized_db)

        assert len(results) == 2
        keys = [r["openlibrary_work_key"] for r in results]
        assert "/works/OL1W" in keys
        assert "/works/OL3W" in keys

    async def test_get_books_by_status_empty(self, initialized_db: Path) -> None:
        """Test that get_books_by_status returns empty list when no books match."""
        results = await get_books_by_status("completed", initialized_db)
        assert results == []

    async def test_get_status_counts(self, initialized_db: Path) -> None:
        """Test that get_status_counts returns correct counts for each status."""
        await set_book_status(
            openlibrary_work_key="/works/OL1W",
            status="to_read",
            title="Book One",
            author_name=["Author A"],
            db_path=initialized_db,
        )
        await set_book_status(
            openlibrary_work_key="/works/OL2W",
            status="to_read",
            title="Book Two",
            author_name=["Author B"],
            db_path=initialized_db,
        )
        await set_book_status(
            openlibrary_work_key="/works/OL3W",
            status="completed",
            title="Book Three",
            author_name=["Author C"],
            db_path=initialized_db,
        )

        counts = await get_status_counts(initialized_db)

        assert counts == {
            "to_read": 2,
            "did_not_finish": 0,
            "completed": 1,
        }

    async def test_get_status_counts_empty(self, initialized_db: Path) -> None:
        """Test that get_status_counts returns zeros when no books exist."""
        counts = await get_status_counts(initialized_db)

        assert counts == {
            "to_read": 0,
            "did_not_finish": 0,
            "completed": 0,
        }

    async def test_status_enum_constraint(self, initialized_db: Path) -> None:
        """Test that invalid status values are rejected by the database."""
        from api.database import DatabaseError

        with pytest.raises(DatabaseError):
            await set_book_status(
                openlibrary_work_key="/works/OL123W",
                status="invalid_status",
                title="Test Book",
                author_name=["Author One"],
                db_path=initialized_db,
            )
