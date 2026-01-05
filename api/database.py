"""Database module for SQLite connection and table management."""

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
    try:
        yield db
    finally:
        await db.close()


async def init_database(db_path: Optional[Path] = None) -> None:
    """Initialize the database with required tables."""
    async with get_db_connection(db_path) as db:
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

        # Book reading status table
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS book_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                openlibrary_work_key TEXT UNIQUE NOT NULL,
                status TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
        await db.execute(
            "CREATE INDEX IF NOT EXISTS idx_openlibrary_work_key ON book_status(openlibrary_work_key)"
        )
        await db.commit()


async def clear_expired_cache(db_path: Optional[Path] = None) -> int:
    """Remove expired cache entries. Returns the number of rows deleted."""
    async with get_db_connection(db_path) as db:
        cursor = await db.execute("DELETE FROM search_cache WHERE expires_at < datetime('now')")
        await db.commit()
        return cursor.rowcount


# Book status operations


async def get_book_status(
    openlibrary_work_key: str, db_path: Optional[Path] = None
) -> Optional[dict[str, Any]]:
    """Get the reading status for a book.

    Args:
        openlibrary_work_key: The OpenLibrary work key (e.g., 'OL123W')
        db_path: Optional database path for testing

    Returns:
        Dictionary with status data or None if not found
    """
    async with get_db_connection(db_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM book_status WHERE openlibrary_work_key = ?",
            (openlibrary_work_key,),
        )
        row = await cursor.fetchone()
        if row:
            return dict(row)
        return None


async def set_book_status(
    openlibrary_work_key: str, status: str, db_path: Optional[Path] = None
) -> dict[str, Any]:
    """Set or update the reading status for a book.

    Args:
        openlibrary_work_key: The OpenLibrary work key (e.g., 'OL123W')
        status: The reading status ('to_read', 'did_not_finish', 'completed')
        db_path: Optional database path for testing

    Returns:
        Dictionary with the updated status data
    """
    now = datetime.utcnow().isoformat()
    async with get_db_connection(db_path) as db:
        db.row_factory = aiosqlite.Row
        await db.execute(
            """
            INSERT INTO book_status (openlibrary_work_key, status, created_at, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(openlibrary_work_key) DO UPDATE SET
                status = excluded.status,
                updated_at = excluded.updated_at
            """,
            (openlibrary_work_key, status, now, now),
        )
        await db.commit()

        cursor = await db.execute(
            "SELECT * FROM book_status WHERE openlibrary_work_key = ?",
            (openlibrary_work_key,),
        )
        row = await cursor.fetchone()
        return dict(row)


async def delete_book_status(openlibrary_work_key: str, db_path: Optional[Path] = None) -> bool:
    """Delete the reading status for a book.

    Args:
        openlibrary_work_key: The OpenLibrary work key (e.g., 'OL123W')
        db_path: Optional database path for testing

    Returns:
        True if a row was deleted, False if no row existed
    """
    async with get_db_connection(db_path) as db:
        cursor = await db.execute(
            "DELETE FROM book_status WHERE openlibrary_work_key = ?",
            (openlibrary_work_key,),
        )
        await db.commit()
        return cursor.rowcount > 0


async def get_all_book_statuses(
    db_path: Optional[Path] = None,
) -> list[dict[str, Any]]:
    """Get all book statuses.

    Args:
        db_path: Optional database path for testing

    Returns:
        List of dictionaries with status data
    """
    async with get_db_connection(db_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM book_status ORDER BY updated_at DESC")
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


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
        # Create placeholders for the IN clause
        placeholders = ",".join("?" * len(openlibrary_work_keys))
        cursor = await db.execute(
            f"SELECT openlibrary_work_key, status FROM book_status WHERE openlibrary_work_key IN ({placeholders})",
            openlibrary_work_keys,
        )
        rows = await cursor.fetchall()
        return {row["openlibrary_work_key"]: row["status"] for row in rows}
