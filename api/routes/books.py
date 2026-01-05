"""Book search route handlers."""

from fastapi import APIRouter, HTTPException, Query

from api.models.schemas import SearchResponse, ErrorResponse
from api.services.cache import get_cached_response, store_cached_response
from api.services.openlibrary import (
    search_books,
    parse_search_response,
    OpenLibraryError,
)

router = APIRouter(prefix="/api/books", tags=["books"])


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
        return parse_search_response(cached_response, page, limit)

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

    return parse_search_response(raw_response, page, limit)
