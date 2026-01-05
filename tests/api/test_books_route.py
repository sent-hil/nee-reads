"""Tests for books route."""

import pytest
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient

from api.services.openlibrary import OpenLibraryError


class TestSearchEndpoint:
    """Tests for /api/books/search endpoint."""

    async def test_returns_search_results(
        self, client: AsyncClient, sample_openlibrary_response: dict
    ) -> None:
        """Test that search returns results from API."""
        with (
            patch("api.routes.books.get_cached_response", new_callable=AsyncMock) as mock_cache_get,
            patch(
                "api.routes.books.store_cached_response", new_callable=AsyncMock
            ) as mock_cache_store,
            patch("api.routes.books.search_books", new_callable=AsyncMock) as mock_search,
        ):
            mock_cache_get.return_value = None
            mock_search.return_value = sample_openlibrary_response

            response = await client.get("/api/books/search", params={"q": "tolkien"})

            assert response.status_code == 200
            data = response.json()
            assert "books" in data
            assert len(data["books"]) == 2
            assert data["total"] == 2

    async def test_returns_cached_response(
        self, client: AsyncClient, sample_openlibrary_response: dict
    ) -> None:
        """Test that cached response is returned when available."""
        with (
            patch("api.routes.books.get_cached_response", new_callable=AsyncMock) as mock_cache_get,
            patch("api.routes.books.search_books", new_callable=AsyncMock) as mock_search,
        ):
            mock_cache_get.return_value = sample_openlibrary_response

            response = await client.get("/api/books/search", params={"q": "cached"})

            assert response.status_code == 200
            mock_search.assert_not_called()

    async def test_stores_response_in_cache(
        self, client: AsyncClient, sample_openlibrary_response: dict
    ) -> None:
        """Test that API response is stored in cache."""
        with (
            patch("api.routes.books.get_cached_response", new_callable=AsyncMock) as mock_cache_get,
            patch(
                "api.routes.books.store_cached_response", new_callable=AsyncMock
            ) as mock_cache_store,
            patch("api.routes.books.search_books", new_callable=AsyncMock) as mock_search,
        ):
            mock_cache_get.return_value = None
            mock_search.return_value = sample_openlibrary_response

            await client.get("/api/books/search", params={"q": "test"})

            mock_cache_store.assert_called_once()

    async def test_requires_query_parameter(self, client: AsyncClient) -> None:
        """Test that query parameter is required."""
        response = await client.get("/api/books/search")
        assert response.status_code == 422

    async def test_validates_empty_query(self, client: AsyncClient) -> None:
        """Test that empty query is rejected."""
        response = await client.get("/api/books/search", params={"q": ""})
        assert response.status_code == 422

    async def test_validates_page_parameter(self, client: AsyncClient) -> None:
        """Test that page parameter must be positive."""
        response = await client.get("/api/books/search", params={"q": "test", "page": 0})
        assert response.status_code == 422

        response = await client.get("/api/books/search", params={"q": "test", "page": -1})
        assert response.status_code == 422

    async def test_validates_limit_parameter(self, client: AsyncClient) -> None:
        """Test that limit parameter is validated."""
        response = await client.get("/api/books/search", params={"q": "test", "limit": 0})
        assert response.status_code == 422

        response = await client.get("/api/books/search", params={"q": "test", "limit": 101})
        assert response.status_code == 422

    async def test_accepts_valid_pagination(
        self, client: AsyncClient, sample_openlibrary_response: dict
    ) -> None:
        """Test that valid pagination parameters are accepted."""
        with (
            patch("api.routes.books.get_cached_response", new_callable=AsyncMock) as mock_cache_get,
            patch("api.routes.books.store_cached_response", new_callable=AsyncMock),
            patch("api.routes.books.search_books", new_callable=AsyncMock) as mock_search,
        ):
            mock_cache_get.return_value = None
            mock_search.return_value = sample_openlibrary_response

            response = await client.get(
                "/api/books/search", params={"q": "test", "page": 2, "limit": 50}
            )

            assert response.status_code == 200
            mock_search.assert_called_once_with("test", 2, 50)

    async def test_returns_504_on_timeout(self, client: AsyncClient) -> None:
        """Test that 504 is returned on API timeout."""
        with (
            patch("api.routes.books.get_cached_response", new_callable=AsyncMock) as mock_cache_get,
            patch("api.routes.books.search_books", new_callable=AsyncMock) as mock_search,
        ):
            mock_cache_get.return_value = None
            mock_search.side_effect = OpenLibraryError("Request timed out")

            response = await client.get("/api/books/search", params={"q": "timeout"})

            assert response.status_code == 504

    async def test_returns_502_on_api_error(self, client: AsyncClient) -> None:
        """Test that 502 is returned on API error."""
        with (
            patch("api.routes.books.get_cached_response", new_callable=AsyncMock) as mock_cache_get,
            patch("api.routes.books.search_books", new_callable=AsyncMock) as mock_search,
        ):
            mock_cache_get.return_value = None
            mock_search.side_effect = OpenLibraryError("API Error", status_code=500)

            response = await client.get("/api/books/search", params={"q": "error"})

            assert response.status_code == 502

    async def test_returns_empty_books_for_no_results(
        self, client: AsyncClient, sample_openlibrary_empty_response: dict
    ) -> None:
        """Test that empty books list is returned for no results."""
        with (
            patch("api.routes.books.get_cached_response", new_callable=AsyncMock) as mock_cache_get,
            patch("api.routes.books.store_cached_response", new_callable=AsyncMock),
            patch("api.routes.books.search_books", new_callable=AsyncMock) as mock_search,
        ):
            mock_cache_get.return_value = None
            mock_search.return_value = sample_openlibrary_empty_response

            response = await client.get("/api/books/search", params={"q": "nonexistent12345"})

            assert response.status_code == 200
            data = response.json()
            assert data["books"] == []
            assert data["total"] == 0

    async def test_response_includes_pagination_info(
        self, client: AsyncClient, sample_openlibrary_response: dict
    ) -> None:
        """Test that response includes pagination information."""
        with (
            patch("api.routes.books.get_cached_response", new_callable=AsyncMock) as mock_cache_get,
            patch("api.routes.books.store_cached_response", new_callable=AsyncMock),
            patch("api.routes.books.search_books", new_callable=AsyncMock) as mock_search,
        ):
            mock_cache_get.return_value = None
            mock_search.return_value = sample_openlibrary_response

            response = await client.get(
                "/api/books/search", params={"q": "test", "page": 1, "limit": 100}
            )

            assert response.status_code == 200
            data = response.json()
            assert "page" in data
            assert "total_pages" in data
            assert "total" in data
            assert data["page"] == 1

    async def test_book_has_expected_fields(
        self, client: AsyncClient, sample_openlibrary_response: dict
    ) -> None:
        """Test that books have expected fields."""
        with (
            patch("api.routes.books.get_cached_response", new_callable=AsyncMock) as mock_cache_get,
            patch("api.routes.books.store_cached_response", new_callable=AsyncMock),
            patch("api.routes.books.search_books", new_callable=AsyncMock) as mock_search,
        ):
            mock_cache_get.return_value = None
            mock_search.return_value = sample_openlibrary_response

            response = await client.get("/api/books/search", params={"q": "test"})

            assert response.status_code == 200
            book = response.json()["books"][0]
            assert "openlibrary_work_key" in book
            assert "title" in book
            assert "author_name" in book
            assert "cover_url" in book
            assert "first_publish_year" in book
