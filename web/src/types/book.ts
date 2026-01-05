/**
 * Book type definitions
 */

export interface Book {
  openlibrary_work_key: string;
  title: string;
  author_name: string[];
  cover_url: string | null;
  first_publish_year: number | null;
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
