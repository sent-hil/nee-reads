"""Book search route handlers."""

from fastapi import APIRouter, HTTPException, Query

from api.models.schemas import SearchResponse, ErrorResponse, ReadingStatus
from api.services.cache import get_cached_response, store_cached_response
from api.services.openlibrary import (
    search_books,
    parse_search_response,
    OpenLibraryError,
)
from api.database import get_book_statuses_batch

router = APIRouter(prefix="/api/books", tags=["books"])


async def enrich_books_with_status(response: SearchResponse) -> SearchResponse:
    """Add reading status to books from the database.

    Args:
        response: SearchResponse with books to enrich

    Returns:
        SearchResponse with status field populated for books that have a status
    """
    if not response.books:
        return response

    # Get all book keys
    book_keys = [book.openlibrary_work_key for book in response.books]

    # Fetch statuses in a single batch query
    statuses = await get_book_statuses_batch(book_keys)

    # Update books with their status
    for book in response.books:
        if book.openlibrary_work_key in statuses:
            book.status = ReadingStatus(statuses[book.openlibrary_work_key])

    return response


@router.get(
    "/search",
    response_model=SearchResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request parameters"},
        502: {"model": ErrorResponse, "description": "OpenLibrary API error"},
        504: {"model": ErrorResponse, "description": "OpenLibrary API timeout"},
    },
)
async def search(
    q: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(100, ge=1, le=100, description="Results per page"),
) -> SearchResponse:
    """Search for books by title or author.

    Args:
        q: Search query string
        page: Page number (1-indexed)
        limit: Number of results per page (max 100)

    Returns:
        SearchResponse with list of books and pagination info
    """
    # Check cache first
    cached_response = await get_cached_response(q, page, limit)
    if cached_response:
        response = parse_search_response(cached_response, page, limit)
        return await enrich_books_with_status(response)

    # Fetch from OpenLibrary API
    try:
        raw_response = await search_books(q, page, limit)
    except OpenLibraryError as e:
        if "timed out" in e.message.lower():
            raise HTTPException(status_code=504, detail=e.message)
        elif e.status_code:
            raise HTTPException(status_code=502, detail=e.message)
        else:
            raise HTTPException(status_code=502, detail=e.message)

    # Store in cache
    await store_cached_response(q, page, limit, raw_response)

    response = parse_search_response(raw_response, page, limit)
    return await enrich_books_with_status(response)
