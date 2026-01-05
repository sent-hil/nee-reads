"""OpenLibrary API client service."""

import httpx
from typing import Any, Optional

from api.models.schemas import Book, SearchResponse

OPENLIBRARY_SEARCH_URL = "https://openlibrary.org/search.json"
OPENLIBRARY_COVER_URL = "https://covers.openlibrary.org/b"

# Default timeout in seconds
DEFAULT_TIMEOUT = 30.0


class OpenLibraryError(Exception):
    """Exception raised for OpenLibrary API errors."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


def build_cover_url(doc: dict[str, Any]) -> Optional[str]:
    """Build cover URL from document data.

    Priority:
    1. cover_i (cover ID) - most reliable
    2. isbn - fallback if no cover_i
    """
    if cover_i := doc.get("cover_i"):
        return f"{OPENLIBRARY_COVER_URL}/id/{cover_i}-L.jpg"

    if isbn_list := doc.get("isbn"):
        if isbn_list and len(isbn_list) > 0:
            return f"{OPENLIBRARY_COVER_URL}/isbn/{isbn_list[0]}-L.jpg"

    return None


def parse_book_from_doc(doc: dict[str, Any]) -> Book:
    """Parse an OpenLibrary document into a Book model."""
    return Book(
        openlibrary_work_key=doc.get("key", ""),
        title=doc.get("title", "Unknown Title"),
        author_name=doc.get("author_name", []),
        cover_url=build_cover_url(doc),
        first_publish_year=doc.get("first_publish_year"),
    )


async def search_books(
    query: str,
    page: int = 1,
    limit: int = 100,
    client: Optional[httpx.AsyncClient] = None,
) -> dict[str, Any]:
    """Search for books using OpenLibrary API.

    Args:
        query: Search query string
        page: Page number (1-indexed)
        limit: Number of results per page
        client: Optional httpx client for testing

    Returns:
        Raw API response as dictionary

    Raises:
        OpenLibraryError: If API request fails
    """
    params = {
        "q": query,
        "page": page,
        "limit": limit,
    }

    should_close_client = client is None
    if client is None:
        client = httpx.AsyncClient(timeout=DEFAULT_TIMEOUT)

    try:
        response = await client.get(OPENLIBRARY_SEARCH_URL, params=params)
        response.raise_for_status()
        return response.json()
    except httpx.TimeoutException as e:
        raise OpenLibraryError("Request to OpenLibrary timed out") from e
    except httpx.HTTPStatusError as e:
        raise OpenLibraryError(
            f"OpenLibrary API error: {e.response.status_code}",
            status_code=e.response.status_code,
        ) from e
    except httpx.RequestError as e:
        raise OpenLibraryError(f"Failed to connect to OpenLibrary: {str(e)}") from e
    finally:
        if should_close_client:
            await client.aclose()


def parse_search_response(raw_response: dict[str, Any], page: int, limit: int) -> SearchResponse:
    """Parse raw OpenLibrary response into SearchResponse.

    Args:
        raw_response: Raw JSON response from OpenLibrary API
        page: Current page number
        limit: Results per page

    Returns:
        SearchResponse model with parsed books
    """
    docs = raw_response.get("docs", [])
    total = raw_response.get("numFound", raw_response.get("num_found", 0))

    books = [parse_book_from_doc(doc) for doc in docs]
    total_pages = (total + limit - 1) // limit if limit > 0 else 0

    return SearchResponse(
        books=books,
        total=total,
        page=page,
        total_pages=total_pages,
    )
