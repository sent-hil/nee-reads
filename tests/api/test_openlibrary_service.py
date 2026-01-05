"""Tests for OpenLibrary service."""

import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock

from api.services.openlibrary import (
    build_cover_url,
    parse_book_from_doc,
    search_books,
    parse_search_response,
    OpenLibraryError,
    OPENLIBRARY_COVER_URL,
)
from api.models.schemas import Book, SearchResponse


class TestBuildCoverUrl:
    """Tests for build_cover_url function."""

    def test_uses_cover_i_when_available(self) -> None:
        """Test that cover_i is preferred for cover URL."""
        doc = {"cover_i": 12345, "isbn": ["9780123456789"]}
        url = build_cover_url(doc)
        assert url == f"{OPENLIBRARY_COVER_URL}/id/12345-L.jpg"

    def test_falls_back_to_isbn(self) -> None:
        """Test that ISBN is used when cover_i is not available."""
        doc = {"isbn": ["9780123456789", "9780987654321"]}
        url = build_cover_url(doc)
        assert url == f"{OPENLIBRARY_COVER_URL}/isbn/9780123456789-L.jpg"

    def test_returns_none_when_no_cover_info(self) -> None:
        """Test that None is returned when no cover info available."""
        doc = {"title": "No Cover Book"}
        url = build_cover_url(doc)
        assert url is None

    def test_returns_none_for_empty_isbn_list(self) -> None:
        """Test that None is returned for empty ISBN list."""
        doc = {"isbn": []}
        url = build_cover_url(doc)
        assert url is None

    def test_handles_zero_cover_i(self) -> None:
        """Test that zero cover_i is treated as falsy."""
        doc = {"cover_i": 0, "isbn": ["9780123456789"]}
        url = build_cover_url(doc)
        # 0 is falsy, so should fall back to ISBN
        assert url == f"{OPENLIBRARY_COVER_URL}/isbn/9780123456789-L.jpg"


class TestParseBookFromDoc:
    """Tests for parse_book_from_doc function."""

    def test_parses_complete_doc(self) -> None:
        """Test parsing a complete document."""
        doc = {
            "key": "/works/OL12345W",
            "title": "Test Book",
            "author_name": ["Author One", "Author Two"],
            "cover_i": 98765,
            "first_publish_year": 2020,
        }
        book = parse_book_from_doc(doc)

        assert book.openlibrary_work_key == "/works/OL12345W"
        assert book.title == "Test Book"
        assert book.author_name == ["Author One", "Author Two"]
        assert book.cover_url == f"{OPENLIBRARY_COVER_URL}/id/98765-L.jpg"
        assert book.first_publish_year == 2020

    def test_handles_missing_optional_fields(self) -> None:
        """Test parsing a document with missing optional fields."""
        doc = {"key": "/works/OL12345W", "title": "Minimal Book"}
        book = parse_book_from_doc(doc)

        assert book.openlibrary_work_key == "/works/OL12345W"
        assert book.title == "Minimal Book"
        assert book.author_name == []
        assert book.cover_url is None
        assert book.first_publish_year is None

    def test_handles_empty_doc(self) -> None:
        """Test parsing an empty document."""
        doc = {}
        book = parse_book_from_doc(doc)

        assert book.openlibrary_work_key == ""
        assert book.title == "Unknown Title"
        assert book.author_name == []
        assert book.cover_url is None
        assert book.first_publish_year is None

    def test_returns_book_instance(self) -> None:
        """Test that function returns a Book instance."""
        doc = {"key": "/works/OL1W", "title": "A Book"}
        book = parse_book_from_doc(doc)
        assert isinstance(book, Book)


class TestSearchBooks:
    """Tests for search_books function."""

    async def test_makes_request_with_correct_params(self) -> None:
        """Test that request is made with correct parameters."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"numFound": 0, "docs": []}
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.get.return_value = mock_response

        await search_books("test query", page=2, limit=50, client=mock_client)

        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert call_args[1]["params"]["q"] == "test query"
        assert call_args[1]["params"]["page"] == 2
        assert call_args[1]["params"]["limit"] == 50

    async def test_returns_json_response(self) -> None:
        """Test that JSON response is returned."""
        expected = {"numFound": 5, "docs": [{"title": "Book"}]}

        mock_response = MagicMock()
        mock_response.json.return_value = expected
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.get.return_value = mock_response

        result = await search_books("test", client=mock_client)
        assert result == expected

    async def test_raises_on_timeout(self) -> None:
        """Test that OpenLibraryError is raised on timeout."""
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.get.side_effect = httpx.TimeoutException("Timeout")

        with pytest.raises(OpenLibraryError) as exc_info:
            await search_books("test", client=mock_client)

        assert "timed out" in exc_info.value.message.lower()

    async def test_raises_on_http_error(self) -> None:
        """Test that OpenLibraryError is raised on HTTP error."""
        mock_request = MagicMock(spec=httpx.Request)
        mock_response = MagicMock()
        mock_response.status_code = 500

        http_error = httpx.HTTPStatusError(
            "Server Error", request=mock_request, response=mock_response
        )
        mock_response.raise_for_status.side_effect = http_error

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.get.return_value = mock_response

        with pytest.raises(OpenLibraryError) as exc_info:
            await search_books("test", client=mock_client)

        assert exc_info.value.status_code == 500

    async def test_raises_on_request_error(self) -> None:
        """Test that OpenLibraryError is raised on request error."""
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.get.side_effect = httpx.RequestError("Connection failed")

        with pytest.raises(OpenLibraryError) as exc_info:
            await search_books("test", client=mock_client)

        assert "failed to connect" in exc_info.value.message.lower()


class TestParseSearchResponse:
    """Tests for parse_search_response function."""

    def test_parses_response_with_results(self, sample_openlibrary_response: dict) -> None:
        """Test parsing a response with results."""
        result = parse_search_response(sample_openlibrary_response, page=1, limit=100)

        assert isinstance(result, SearchResponse)
        assert len(result.books) == 2
        assert result.total == 2
        assert result.page == 1
        assert result.total_pages == 1

    def test_parses_empty_response(self, sample_openlibrary_empty_response: dict) -> None:
        """Test parsing an empty response."""
        result = parse_search_response(sample_openlibrary_empty_response, page=1, limit=100)

        assert len(result.books) == 0
        assert result.total == 0
        assert result.page == 1
        assert result.total_pages == 0

    def test_calculates_total_pages_correctly(self) -> None:
        """Test that total pages is calculated correctly."""
        response = {"numFound": 250, "docs": []}

        result = parse_search_response(response, page=1, limit=100)
        assert result.total_pages == 3

        result = parse_search_response(response, page=1, limit=50)
        assert result.total_pages == 5

    def test_handles_num_found_key_variation(self) -> None:
        """Test that both numFound and num_found keys work."""
        response1 = {"numFound": 10, "docs": []}
        response2 = {"num_found": 10, "docs": []}

        result1 = parse_search_response(response1, page=1, limit=100)
        result2 = parse_search_response(response2, page=1, limit=100)

        assert result1.total == 10
        assert result2.total == 10

    def test_parses_book_details(self, sample_openlibrary_response: dict) -> None:
        """Test that book details are parsed correctly."""
        result = parse_search_response(sample_openlibrary_response, page=1, limit=100)

        book = result.books[0]
        assert book.openlibrary_work_key == "/works/OL27448W"
        assert book.title == "The Lord of the Rings"
        assert book.author_name == ["J. R. R. Tolkien"]
        assert book.first_publish_year == 1954
