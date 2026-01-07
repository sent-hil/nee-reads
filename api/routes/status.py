"""Book status route handlers."""

import logging
from fastapi import APIRouter, HTTPException, Path

from api.models.schemas import (
    BookStatusRequest,
    BookStatusResponse,
    BookStatusListResponse,
    ErrorResponse,
    ReadingStatus,
)
from api.database import (
    get_book_status,
    set_book_status,
    delete_book_status,
    get_all_book_statuses,
    DatabaseError,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/status", tags=["status"])


@router.get(
    "",
    response_model=BookStatusListResponse,
    summary="Get all book statuses",
    responses={
        500: {"model": ErrorResponse, "description": "Database error"},
    },
)
async def list_statuses() -> BookStatusListResponse:
    """Get all book reading statuses.

    Returns:
        List of all book statuses ordered by most recently updated
    """
    try:
        statuses = await get_all_book_statuses()
        return BookStatusListResponse(
            statuses=[
                BookStatusResponse(
                    openlibrary_work_key=s["openlibrary_work_key"],
                    title=s["title"],
                    author_name=s["author_name"],
                    cover_url=s["cover_url"],
                    first_publish_year=s["first_publish_year"],
                    status=ReadingStatus(s["status"]),
                    created_at=s["created_at"],
                    updated_at=s["updated_at"],
                )
                for s in statuses
            ]
        )
    except DatabaseError as e:
        logger.error(f"Database error listing statuses: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{openlibrary_work_key:path}",
    response_model=BookStatusResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Book status not found"},
        500: {"model": ErrorResponse, "description": "Database error"},
    },
    summary="Get book status",
)
async def get_status(
    openlibrary_work_key: str = Path(..., description="OpenLibrary work key"),
) -> BookStatusResponse:
    """Get the reading status for a specific book.

    Args:
        openlibrary_work_key: The OpenLibrary work key (e.g., '/works/OL123W')

    Returns:
        BookStatusResponse with the current status and book metadata
    """
    try:
        status = await get_book_status(openlibrary_work_key)
        if not status:
            raise HTTPException(status_code=404, detail="Book status not found")

        return BookStatusResponse(
            openlibrary_work_key=status["openlibrary_work_key"],
            title=status["title"],
            author_name=status["author_name"],
            cover_url=status["cover_url"],
            first_publish_year=status["first_publish_year"],
            status=ReadingStatus(status["status"]),
            created_at=status["created_at"],
            updated_at=status["updated_at"],
        )
    except HTTPException:
        raise
    except DatabaseError as e:
        logger.error(f"Database error getting status for {openlibrary_work_key}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/{openlibrary_work_key:path}",
    response_model=BookStatusResponse,
    summary="Set book status",
    responses={
        500: {"model": ErrorResponse, "description": "Database error"},
    },
)
async def update_status(
    request: BookStatusRequest,
    openlibrary_work_key: str = Path(..., description="OpenLibrary work key"),
) -> BookStatusResponse:
    """Set or update the reading status for a book.

    Args:
        openlibrary_work_key: The OpenLibrary work key (e.g., '/works/OL123W')
        request: The status and book metadata to set

    Returns:
        BookStatusResponse with the updated status and book metadata
    """
    try:
        status = await set_book_status(
            openlibrary_work_key=openlibrary_work_key,
            status=request.status.value,
            title=request.title,
            author_name=request.author_name,
            cover_url=request.cover_url,
            first_publish_year=request.first_publish_year,
        )

        return BookStatusResponse(
            openlibrary_work_key=status["openlibrary_work_key"],
            title=status["title"],
            author_name=status["author_name"],
            cover_url=status["cover_url"],
            first_publish_year=status["first_publish_year"],
            status=ReadingStatus(status["status"]),
            created_at=status["created_at"],
            updated_at=status["updated_at"],
        )
    except DatabaseError as e:
        logger.error(f"Database error setting status for {openlibrary_work_key}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/{openlibrary_work_key:path}",
    status_code=204,
    responses={
        404: {"model": ErrorResponse, "description": "Book status not found"},
        500: {"model": ErrorResponse, "description": "Database error"},
    },
    summary="Delete book status",
)
async def remove_status(
    openlibrary_work_key: str = Path(..., description="OpenLibrary work key"),
) -> None:
    """Delete the reading status for a book.

    Args:
        openlibrary_work_key: The OpenLibrary work key (e.g., '/works/OL123W')
    """
    try:
        deleted = await delete_book_status(openlibrary_work_key)
        if not deleted:
            raise HTTPException(status_code=404, detail="Book status not found")
    except HTTPException:
        raise
    except DatabaseError as e:
        logger.error(f"Database error deleting status for {openlibrary_work_key}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
