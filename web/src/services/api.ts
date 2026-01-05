/**
 * API client for book search
 */

import type { SearchResponse, BookStatus, BookStatusListResponse, ReadingStatus } from '../types/book';

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
  const response = await fetch(
    `${API_BASE_URL}/status/${encodeURIComponent(openlibraryWorkKey)}`
  );

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
  status: ReadingStatus
): Promise<BookStatus> {
  const response = await fetch(
    `${API_BASE_URL}/status/${encodeURIComponent(openlibraryWorkKey)}`,
    {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ status }),
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
  const response = await fetch(
    `${API_BASE_URL}/status/${encodeURIComponent(openlibraryWorkKey)}`,
    {
      method: 'DELETE',
    }
  );

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
