"""Cache service for storing and retrieving API responses."""

import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

from api.database import get_db_connection

# Cache TTL in hours
CACHE_TTL_HOURS = 24


def generate_cache_key(query: str, page: int, limit: int) -> str:
    """Generate a unique hash for the cache key."""
    normalized_query = query.strip().lower()
    key_string = f"{normalized_query}:{page}:{limit}"
    return hashlib.sha256(key_string.encode()).hexdigest()


async def get_cached_response(
    query: str, page: int, limit: int, db_path: Optional[Path] = None
) -> Optional[dict[str, Any]]:
    """Retrieve cached response if it exists and is not expired."""
    query_hash = generate_cache_key(query, page, limit)

    async with get_db_connection(db_path) as db:
        db.row_factory = _dict_factory
        cursor = await db.execute(
            """
            SELECT response_json FROM search_cache
            WHERE query_hash = ? AND expires_at > datetime('now')
            """,
            (query_hash,),
        )
        row = await cursor.fetchone()

        if row:
            return json.loads(row["response_json"])

    return None


async def store_cached_response(
    query: str,
    page: int,
    limit: int,
    response: dict[str, Any],
    db_path: Optional[Path] = None,
) -> None:
    """Store a response in the cache."""
    query_hash = generate_cache_key(query, page, limit)
    response_json = json.dumps(response)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=CACHE_TTL_HOURS)

    async with get_db_connection(db_path) as db:
        await db.execute(
            """
            INSERT OR REPLACE INTO search_cache
            (query_hash, query, page, limit_val, response_json, expires_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (query_hash, query, page, limit, response_json, expires_at.isoformat()),
        )
        await db.commit()


async def invalidate_cache(
    query: str, page: int, limit: int, db_path: Optional[Path] = None
) -> bool:
    """Invalidate a specific cache entry. Returns True if entry was deleted."""
    query_hash = generate_cache_key(query, page, limit)

    async with get_db_connection(db_path) as db:
        cursor = await db.execute("DELETE FROM search_cache WHERE query_hash = ?", (query_hash,))
        await db.commit()
        return cursor.rowcount > 0


async def clear_all_cache(db_path: Optional[Path] = None) -> int:
    """Clear all cache entries. Returns number of entries deleted."""
    async with get_db_connection(db_path) as db:
        cursor = await db.execute("DELETE FROM search_cache")
        await db.commit()
        return cursor.rowcount


def _dict_factory(cursor: Any, row: tuple) -> dict[str, Any]:
    """Convert database row to dictionary."""
    fields = [column[0] for column in cursor.description]
    return dict(zip(fields, row))
