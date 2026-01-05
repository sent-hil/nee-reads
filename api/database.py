"""Database module for SQLite connection and table management."""

import json
import aiosqlite
from pathlib import Path
from typing import Optional, Any
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from datetime import datetime

# Default database path - can be overridden for testing
DATABASE_PATH = Path("data/database.db")


@asynccontextmanager
async def get_db_connection(
    db_path: Optional[Path] = None,
) -> AsyncGenerator[aiosqlite.Connection, None]:
    """Get a database connection as a context manager."""
    path = db_path or DATABASE_PATH
    db = await aiosqlite.connect(str(path))
    # Enable foreign key support
    await db.execute("PRAGMA foreign_keys = ON")
    try:
        yield db
    finally:
        await db.close()


async def init_database(db_path: Optional[Path] = None) -> None:
    """Initialize the database with required tables."""
    async with get_db_connection(db_path) as db:
        # Search cache table
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS search_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_hash TEXT UNIQUE NOT NULL,
                query TEXT NOT NULL,
                page INTEGER NOT NULL,
                limit_val INTEGER NOT NULL,
                response_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL
            )
        """
        )
        await db.execute("CREATE INDEX IF NOT EXISTS idx_query_hash ON search_cache(query_hash)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_expires_at ON search_cache(expires_at)")

        # Books table - stores book metadata
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                openlibrary_work_key TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                author_name TEXT NOT NULL,
                cover_url TEXT,
                first_publish_year INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
        await db.execute(
            "CREATE INDEX IF NOT EXISTS idx_books_openlibrary_work_key ON books(openlibrary_work_key)"
        )

        # Book statuses table - stores reading status for each book
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS book_statuses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER NOT NULL UNIQUE REFERENCES books(id) ON DELETE CASCADE,
                status TEXT NOT NULL CHECK(status IN ('to_read', 'did_not_finish', 'completed')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
        await db.execute(
            "CREATE INDEX IF NOT EXISTS idx_book_statuses_book_id ON book_statuses(book_id)"
        )
        await db.execute(
            "CREATE INDEX IF NOT EXISTS idx_book_statuses_status ON book_statuses(status)"
        )

        await db.commit()


async def clear_expired_cache(db_path: Optional[Path] = None) -> int:
    """Remove expired cache entries. Returns the number of rows deleted."""
    async with get_db_connection(db_path) as db:
        cursor = await db.execute("DELETE FROM search_cache WHERE expires_at < datetime('now')")
        await db.commit()
        return cursor.rowcount


# Book and status operations


async def get_book_status(
    openlibrary_work_key: str, db_path: Optional[Path] = None
) -> Optional[dict[str, Any]]:
    """Get the reading status for a book.

    Args:
        openlibrary_work_key: The OpenLibrary work key (e.g., '/works/OL123W')
        db_path: Optional database path for testing

    Returns:
        Dictionary with book and status data or None if not found
    """
    async with get_db_connection(db_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """
            SELECT b.openlibrary_work_key, b.title, b.author_name, b.cover_url, 
                   b.first_publish_year, bs.status, bs.created_at, bs.updated_at
            FROM books b
            JOIN book_statuses bs ON b.id = bs.book_id
            WHERE b.openlibrary_work_key = ?
            """,
            (openlibrary_work_key,),
        )
        row = await cursor.fetchone()
        if row:
            result = dict(row)
            # Parse author_name from JSON string
            result["author_name"] = json.loads(result["author_name"])
            return result
        return None


async def set_book_status(
    openlibrary_work_key: str,
    status: str,
    title: str,
    author_name: list[str],
    cover_url: Optional[str] = None,
    first_publish_year: Optional[int] = None,
    db_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Set or update the reading status for a book.

    Args:
        openlibrary_work_key: The OpenLibrary work key (e.g., '/works/OL123W')
        status: The reading status ('to_read', 'did_not_finish', 'completed')
        title: Book title
        author_name: List of author names
        cover_url: URL to book cover image
        first_publish_year: Year the book was first published
        db_path: Optional database path for testing

    Returns:
        Dictionary with the updated book and status data
    """
    now = datetime.utcnow().isoformat()
    author_name_json = json.dumps(author_name)

    async with get_db_connection(db_path) as db:
        db.row_factory = aiosqlite.Row

        # Insert or update the book
        await db.execute(
            """
            INSERT INTO books (openlibrary_work_key, title, author_name, cover_url, first_publish_year, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(openlibrary_work_key) DO UPDATE SET
                title = excluded.title,
                author_name = excluded.author_name,
                cover_url = excluded.cover_url,
                first_publish_year = excluded.first_publish_year
            """,
            (openlibrary_work_key, title, author_name_json, cover_url, first_publish_year, now),
        )

        # Get the book ID
        cursor = await db.execute(
            "SELECT id FROM books WHERE openlibrary_work_key = ?",
            (openlibrary_work_key,),
        )
        book_row = await cursor.fetchone()
        book_id = book_row["id"]

        # Insert or update the status
        await db.execute(
            """
            INSERT INTO book_statuses (book_id, status, created_at, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(book_id) DO UPDATE SET
                status = excluded.status,
                updated_at = excluded.updated_at
            """,
            (book_id, status, now, now),
        )
        await db.commit()

        # Return the full book with status
        cursor = await db.execute(
            """
            SELECT b.openlibrary_work_key, b.title, b.author_name, b.cover_url, 
                   b.first_publish_year, bs.status, bs.created_at, bs.updated_at
            FROM books b
            JOIN book_statuses bs ON b.id = bs.book_id
            WHERE b.openlibrary_work_key = ?
            """,
            (openlibrary_work_key,),
        )
        row = await cursor.fetchone()
        result = dict(row)
        result["author_name"] = json.loads(result["author_name"])
        return result


async def delete_book_status(openlibrary_work_key: str, db_path: Optional[Path] = None) -> bool:
    """Delete the reading status for a book and remove the book if orphaned.

    Args:
        openlibrary_work_key: The OpenLibrary work key (e.g., '/works/OL123W')
        db_path: Optional database path for testing

    Returns:
        True if a status was deleted, False if no status existed
    """
    async with get_db_connection(db_path) as db:
        # Get book ID first
        cursor = await db.execute(
            "SELECT id FROM books WHERE openlibrary_work_key = ?",
            (openlibrary_work_key,),
        )
        row = await cursor.fetchone()
        if not row:
            return False

        book_id = row[0]

        # Delete the status
        cursor = await db.execute(
            "DELETE FROM book_statuses WHERE book_id = ?",
            (book_id,),
        )
        status_deleted = cursor.rowcount > 0

        # Delete the book (since it's now orphaned - no status references it)
        await db.execute(
            "DELETE FROM books WHERE id = ?",
            (book_id,),
        )

        await db.commit()
        return status_deleted


async def get_all_book_statuses(
    db_path: Optional[Path] = None,
) -> list[dict[str, Any]]:
    """Get all books with their statuses.

    Args:
        db_path: Optional database path for testing

    Returns:
        List of dictionaries with book and status data
    """
    async with get_db_connection(db_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """
            SELECT b.openlibrary_work_key, b.title, b.author_name, b.cover_url, 
                   b.first_publish_year, bs.status, bs.created_at, bs.updated_at
            FROM books b
            JOIN book_statuses bs ON b.id = bs.book_id
            ORDER BY bs.updated_at DESC
            """
        )
        rows = await cursor.fetchall()
        results = []
        for row in rows:
            result = dict(row)
            result["author_name"] = json.loads(result["author_name"])
            results.append(result)
        return results


async def get_book_statuses_batch(
    openlibrary_work_keys: list[str], db_path: Optional[Path] = None
) -> dict[str, str]:
    """Get reading statuses for multiple books in a single query.

    Args:
        openlibrary_work_keys: List of OpenLibrary work keys
        db_path: Optional database path for testing

    Returns:
        Dictionary mapping openlibrary_work_key to status string
    """
    if not openlibrary_work_keys:
        return {}

    async with get_db_connection(db_path) as db:
        db.row_factory = aiosqlite.Row
        placeholders = ",".join("?" * len(openlibrary_work_keys))
        cursor = await db.execute(
            f"""
            SELECT b.openlibrary_work_key, bs.status 
            FROM books b
            JOIN book_statuses bs ON b.id = bs.book_id
            WHERE b.openlibrary_work_key IN ({placeholders})
            """,
            openlibrary_work_keys,
        )
        rows = await cursor.fetchall()
        return {row["openlibrary_work_key"]: row["status"] for row in rows}


async def get_books_by_status(status: str, db_path: Optional[Path] = None) -> list[dict[str, Any]]:
    """Get all books with a specific reading status.

    Args:
        status: The reading status ('to_read', 'did_not_finish', 'completed')
        db_path: Optional database path for testing

    Returns:
        List of dictionaries with book and status data
    """
    async with get_db_connection(db_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """
            SELECT b.openlibrary_work_key, b.title, b.author_name, b.cover_url, 
                   b.first_publish_year, bs.status, bs.created_at, bs.updated_at
            FROM books b
            JOIN book_statuses bs ON b.id = bs.book_id
            WHERE bs.status = ?
            ORDER BY bs.updated_at DESC
            """,
            (status,),
        )
        rows = await cursor.fetchall()
        results = []
        for row in rows:
            result = dict(row)
            result["author_name"] = json.loads(result["author_name"])
            results.append(result)
        return results


async def get_status_counts(db_path: Optional[Path] = None) -> dict[str, int]:
    """Get count of books for each reading status.

    Args:
        db_path: Optional database path for testing

    Returns:
        Dictionary mapping status to count
    """
    async with get_db_connection(db_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """
            SELECT status, COUNT(*) as count
            FROM book_statuses
            GROUP BY status
            """
        )
        rows = await cursor.fetchall()
        # Initialize with zeros
        counts = {"to_read": 0, "did_not_finish": 0, "completed": 0}
        for row in rows:
            counts[row["status"]] = row["count"]
        return counts
