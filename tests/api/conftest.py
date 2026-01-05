"""Pytest configuration and fixtures for API tests."""

import tempfile
import os
from pathlib import Path
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from api.main import create_app
from api.database import init_database


@pytest.fixture
def temp_db_path() -> Path:
    """Create a temporary database path for testing."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield Path(path)
    # Cleanup
    try:
        os.unlink(path)
    except OSError:
        pass


@pytest_asyncio.fixture
async def initialized_db(temp_db_path: Path) -> AsyncGenerator[Path, None]:
    """Initialize database and return the path."""
    await init_database(temp_db_path)
    yield temp_db_path


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client for the FastAPI app."""
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_openlibrary_response() -> dict:
    """Sample OpenLibrary API response for testing."""
    return {
        "numFound": 2,
        "start": 0,
        "docs": [
            {
                "key": "/works/OL27448W",
                "title": "The Lord of the Rings",
                "author_name": ["J. R. R. Tolkien"],
                "cover_i": 258027,
                "first_publish_year": 1954,
                "isbn": ["9780618640157"],
            },
            {
                "key": "/works/OL262758W",
                "title": "The Hobbit",
                "author_name": ["J. R. R. Tolkien"],
                "first_publish_year": 1937,
                "isbn": ["9780547928227"],
            },
        ],
    }


@pytest.fixture
def sample_openlibrary_empty_response() -> dict:
    """Sample empty OpenLibrary API response for testing."""
    return {
        "numFound": 0,
        "start": 0,
        "docs": [],
    }
