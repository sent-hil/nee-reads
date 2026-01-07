/**
 * API client for book search and library
 */

import type {
  SearchResponse,
  BookStatus,
  BookStatusListResponse,
  ReadingStatus,
  LibraryResponse,
  StatusCounts,
  BookMetadata,
} from '../types/book';

const API_BASE_URL = '/api';

export class ApiError extends Error {
  constructor(
    message: string,
    public statusCode: number
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

export interface SearchParams {
  query: string;
  page?: number;
  limit?: number;
}

export async function searchBooks(
  { query, page = 1, limit = 100 }: SearchParams,
  signal?: AbortSignal
): Promise<SearchResponse> {
  const params = new URLSearchParams({
    q: query,
    page: page.toString(),
    limit: limit.toString(),
  });

  const response = await fetch(`${API_BASE_URL}/books/search?${params}`, {
    signal,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const message = errorData.detail || `HTTP error ${response.status}`;
    throw new ApiError(message, response.status);
  }

  return response.json();
}

// Book status API functions

export async function getBookStatus(
  openlibraryWorkKey: string
): Promise<BookStatus | null> {
  // Don't encode - the key contains slashes (e.g., /works/OL123W) and the backend
  // route uses {openlibrary_work_key:path} to handle this
  const response = await fetch(`${API_BASE_URL}/status${openlibraryWorkKey}`);

  if (response.status === 404) {
    return null;
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const message = errorData.detail || `HTTP error ${response.status}`;
    throw new ApiError(message, response.status);
  }

  return response.json();
}

export async function setBookStatus(
  openlibraryWorkKey: string,
  status: ReadingStatus,
  bookMetadata: BookMetadata
): Promise<BookStatus> {
  // Don't encode - the key contains slashes (e.g., /works/OL123W) and the backend
  // route uses {openlibrary_work_key:path} to handle this
  const response = await fetch(`${API_BASE_URL}/status${openlibraryWorkKey}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        status,
        title: bookMetadata.title,
        author_name: bookMetadata.author_name,
        cover_url: bookMetadata.cover_url,
        first_publish_year: bookMetadata.first_publish_year,
      }),
    }
  );

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const message = errorData.detail || `HTTP error ${response.status}`;
    throw new ApiError(message, response.status);
  }

  return response.json();
}

export async function deleteBookStatus(
  openlibraryWorkKey: string
): Promise<void> {
  // Don't encode - the key contains slashes (e.g., /works/OL123W) and the backend
  // route uses {openlibrary_work_key:path} to handle this
  const response = await fetch(`${API_BASE_URL}/status${openlibraryWorkKey}`, {
    method: 'DELETE',
  });

  if (response.status === 404) {
    return; // Already deleted, treat as success
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const message = errorData.detail || `HTTP error ${response.status}`;
    throw new ApiError(message, response.status);
  }
}

export async function getAllBookStatuses(): Promise<BookStatusListResponse> {
  const response = await fetch(`${API_BASE_URL}/status`);

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const message = errorData.detail || `HTTP error ${response.status}`;
    throw new ApiError(message, response.status);
  }

  return response.json();
}

// Library API functions

/** Map status to URL slug */
const STATUS_TO_SLUG: Record<ReadingStatus, string> = {
  to_read: 'to-read',
  did_not_finish: 'did-not-finish',
  completed: 'completed',
};

export async function getLibraryBooks(
  status: ReadingStatus,
  signal?: AbortSignal
): Promise<LibraryResponse> {
  const slug = STATUS_TO_SLUG[status];
  const response = await fetch(`${API_BASE_URL}/library/${slug}`, { signal });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const message = errorData.detail || `HTTP error ${response.status}`;
    throw new ApiError(message, response.status);
  }

  return response.json();
}

export async function getStatusCounts(
  signal?: AbortSignal
): Promise<StatusCounts> {
  const response = await fetch(`${API_BASE_URL}/library/counts`, { signal });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const message = errorData.detail || `HTTP error ${response.status}`;
    throw new ApiError(message, response.status);
  }

  return response.json();
}
