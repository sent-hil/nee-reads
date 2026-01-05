"""Pydantic models for API request/response schemas."""

from typing import Optional

from pydantic import BaseModel, Field


class Book(BaseModel):
    """Book model representing a book from search results."""

    key: str = Field(..., description="Open Library work key")
    title: str = Field(..., description="Book title")
    author_name: list[str] = Field(default_factory=list, description="List of author names")
    cover_url: Optional[str] = Field(None, description="URL to the book cover image")
    first_publish_year: Optional[int] = Field(None, description="Year the book was first published")


class SearchResponse(BaseModel):
    """Response model for book search endpoint."""

    books: list[Book] = Field(default_factory=list, description="List of books")
    total: int = Field(..., description="Total number of results")
    page: int = Field(..., description="Current page number")
    total_pages: int = Field(..., description="Total number of pages")


class ErrorResponse(BaseModel):
    """Error response model."""

    detail: str = Field(..., description="Error message")
