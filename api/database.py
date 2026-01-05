"""Database module for SQLite connection and table management."""

import aiosqlite
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager
from typing import AsyncGenerator

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
        await db.commit()


async def clear_expired_cache(db_path: Optional[Path] = None) -> int:
    """Remove expired cache entries. Returns the number of rows deleted."""
    async with get_db_connection(db_path) as db:
        cursor = await db.execute("DELETE FROM search_cache WHERE expires_at < datetime('now')")
        await db.commit()
        return cursor.rowcount
