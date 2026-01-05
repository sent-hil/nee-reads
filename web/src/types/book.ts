/**
 * Book type definitions
 */

// Book status types
export type ReadingStatus = 'to_read' | 'did_not_finish' | 'completed';

export interface Book {
  openlibrary_work_key: string;
  title: string;
  author_name: string[];
  cover_url: string | null;
  first_publish_year: number | null;
  status: ReadingStatus | null;
}

export interface SearchResponse {
  books: Book[];
  total: number;
  page: number;
  total_pages: number;
}

export interface SearchState {
  query: string;
  books: Book[];
  total: number;
  page: number;
  totalPages: number;
  isLoading: boolean;
  error: string | null;
  hasSearched: boolean;
}

export interface BookStatus {
  openlibrary_work_key: string;
  title: string;
  author_name: string[];
  cover_url: string | null;
  first_publish_year: number | null;
  status: ReadingStatus;
  created_at: string;
  updated_at: string;
}

export interface BookStatusListResponse {
  statuses: BookStatus[];
}

// Library types

export interface LibraryBook {
  openlibrary_work_key: string;
  title: string;
  author_name: string[];
  cover_url: string | null;
  first_publish_year: number | null;
  status: ReadingStatus;
}

export interface LibraryResponse {
  books: LibraryBook[];
  total: number;
}

export interface StatusCounts {
  to_read: number;
  did_not_finish: number;
  completed: number;
}

// Book metadata for API calls
export interface BookMetadata {
  title: string;
  author_name: string[];
  cover_url: string | null;
  first_publish_year: number | null;
}
