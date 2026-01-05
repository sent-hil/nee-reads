"""Pydantic models for API request/response schemas."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ReadingStatus(str, Enum):
    """Valid reading status values."""

    TO_READ = "to_read"
    DID_NOT_FINISH = "did_not_finish"
    COMPLETED = "completed"


class Book(BaseModel):
    """Book model representing a book from search results."""

    openlibrary_work_key: str = Field(
        ..., description="OpenLibrary work key (e.g., '/works/OL123W')"
    )
    title: str = Field(..., description="Book title")
    author_name: list[str] = Field(default_factory=list, description="List of author names")
    cover_url: Optional[str] = Field(None, description="URL to the book cover image")
    first_publish_year: Optional[int] = Field(None, description="Year the book was first published")
    status: Optional[ReadingStatus] = Field(None, description="Reading status if set")


class SearchResponse(BaseModel):
    """Response model for book search endpoint."""

    books: list[Book] = Field(default_factory=list, description="List of books")
    total: int = Field(..., description="Total number of results")
    page: int = Field(..., description="Current page number")
    total_pages: int = Field(..., description="Total number of pages")


class ErrorResponse(BaseModel):
    """Error response model."""

    detail: str = Field(..., description="Error message")


# Book status models


class BookStatusRequest(BaseModel):
    """Request model for setting book status. Includes book metadata."""

    status: ReadingStatus = Field(..., description="Reading status for the book")
    title: str = Field(..., description="Book title")
    author_name: list[str] = Field(..., description="List of author names")
    cover_url: Optional[str] = Field(None, description="URL to the book cover image")
    first_publish_year: Optional[int] = Field(None, description="Year the book was first published")


class BookStatusResponse(BaseModel):
    """Response model for book status with full book metadata."""

    openlibrary_work_key: str = Field(..., description="OpenLibrary work key")
    title: str = Field(..., description="Book title")
    author_name: list[str] = Field(..., description="List of author names")
    cover_url: Optional[str] = Field(None, description="URL to the book cover image")
    first_publish_year: Optional[int] = Field(None, description="Year the book was first published")
    status: ReadingStatus = Field(..., description="Reading status")
    created_at: str = Field(..., description="When the status was first set")
    updated_at: str = Field(..., description="When the status was last updated")


class BookStatusListResponse(BaseModel):
    """Response model for list of book statuses."""

    statuses: list[BookStatusResponse] = Field(
        default_factory=list, description="List of book statuses"
    )


# Library models


class LibraryBook(BaseModel):
    """Book model for library responses (with status always present)."""

    openlibrary_work_key: str = Field(..., description="OpenLibrary work key")
    title: str = Field(..., description="Book title")
    author_name: list[str] = Field(..., description="List of author names")
    cover_url: Optional[str] = Field(None, description="URL to the book cover image")
    first_publish_year: Optional[int] = Field(None, description="Year the book was first published")
    status: ReadingStatus = Field(..., description="Reading status")


class LibraryResponse(BaseModel):
    """Response model for library endpoint."""

    books: list[LibraryBook] = Field(default_factory=list, description="List of books")
    total: int = Field(..., description="Total number of books in this category")


class StatusCountsResponse(BaseModel):
    """Response model for status counts endpoint."""

    to_read: int = Field(..., description="Number of books in 'to read' status")
    did_not_finish: int = Field(..., description="Number of books in 'didn't finish' status")
    completed: int = Field(..., description="Number of completed books")
