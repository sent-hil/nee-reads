"""Library route handlers."""

from fastapi import APIRouter, HTTPException

from api.models.schemas import (
    LibraryBook,
    LibraryResponse,
    StatusCountsResponse,
    ReadingStatus,
    ErrorResponse,
)
from api.database import (
    get_books_by_status,
    get_status_counts,
)

router = APIRouter(prefix="/api/library", tags=["library"])


# Map URL-friendly status slugs to database values
STATUS_SLUG_MAP = {
    "to-read": "to_read",
    "did-not-finish": "did_not_finish",
    "completed": "completed",
}


@router.get(
    "/counts",
    response_model=StatusCountsResponse,
    summary="Get book counts by status",
)
async def get_counts() -> StatusCountsResponse:
    """Get the count of books in each reading status category.

    Returns:
        StatusCountsResponse with counts for each status
    """
    counts = await get_status_counts()
    return StatusCountsResponse(
        to_read=counts["to_read"],
        did_not_finish=counts["did_not_finish"],
        completed=counts["completed"],
    )


@router.get(
    "/{status}",
    response_model=LibraryResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid status"},
    },
    summary="Get books by status",
)
async def get_library_books(status: str) -> LibraryResponse:
    """Get all books with a specific reading status.

    Args:
        status: The reading status slug ('to-read', 'did-not-finish', 'completed')

    Returns:
        LibraryResponse with list of books
    """
    # Convert URL slug to database status
    db_status = STATUS_SLUG_MAP.get(status)
    if not db_status:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status '{status}'. Valid values: to-read, did-not-finish, completed",
        )

    books = await get_books_by_status(db_status)

    return LibraryResponse(
        books=[
            LibraryBook(
                openlibrary_work_key=book["openlibrary_work_key"],
                title=book["title"],
                author_name=book["author_name"],
                cover_url=book["cover_url"],
                first_publish_year=book["first_publish_year"],
                status=ReadingStatus(book["status"]),
            )
            for book in books
        ],
        total=len(books),
    )
