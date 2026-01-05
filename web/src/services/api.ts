/**
 * API client for book search
 */

import type { SearchResponse } from '../types/book';

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
