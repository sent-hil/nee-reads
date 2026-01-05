/**
 * Main App component
 */

import { useState, useEffect, useCallback, useRef } from 'preact/hooks';
import type { Book, ReadingStatus } from './types/book';
import { searchBooks, ApiError } from './services/api';
import { useDebounce } from './hooks/useDebounce';
import { SearchBar } from './components/SearchBar';
import { BookGrid } from './components/BookGrid';
import { Pagination } from './components/Pagination';
import { EmptyState } from './components/EmptyState';
import { NoResults } from './components/NoResults';
import { LoadingState } from './components/LoadingState';

const DEBOUNCE_DELAY = 500;

interface SearchState {
  books: Book[];
  total: number;
  page: number;
  totalPages: number;
  isLoading: boolean;
  error: string | null;
  hasSearched: boolean;
}

const initialState: SearchState = {
  books: [],
  total: 0,
  page: 1,
  totalPages: 0,
  isLoading: false,
  error: null,
  hasSearched: false,
};

export function App() {
  const [query, setQuery] = useState('');
  const [state, setState] = useState<SearchState>(initialState);
  const abortControllerRef = useRef<AbortController | null>(null);

  const debouncedQuery = useDebounce(query.trim(), DEBOUNCE_DELAY);

  const performSearch = useCallback(
    async (searchQuery: string, page: number) => {
      // Cancel any pending request
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }

      if (!searchQuery) {
        setState(initialState);
        return;
      }

      // Create new abort controller for this request
      const abortController = new AbortController();
      abortControllerRef.current = abortController;

      setState((prev) => ({ ...prev, isLoading: true, error: null }));

      try {
        const response = await searchBooks(
          { query: searchQuery, page },
          abortController.signal
        );
        setState({
          books: response.books,
          total: response.total,
          page: response.page,
          totalPages: response.total_pages,
          isLoading: false,
          error: null,
          hasSearched: true,
        });
      } catch (err) {
        // Ignore aborted requests
        if (err instanceof Error && err.name === 'AbortError') {
          return;
        }
        const message =
          err instanceof ApiError
            ? err.message
            : 'An unexpected error occurred. Please try again.';
        setState((prev) => ({
          ...prev,
          isLoading: false,
          error: message,
          hasSearched: true,
        }));
      }
    },
    []
  );

  // Search when debounced query changes
  useEffect(() => {
    performSearch(debouncedQuery, 1);
  }, [debouncedQuery, performSearch]);

  const handleQueryChange = (newQuery: string) => {
    setQuery(newQuery);
  };

  const handleClear = () => {
    setQuery('');
    setState(initialState);
  };

  const handlePageChange = (newPage: number) => {
    performSearch(debouncedQuery, newPage);
    // Scroll to top when changing pages
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleStatusChange = (openlibraryWorkKey: string, status: ReadingStatus) => {
    // Update the book's status in local state to keep UI in sync
    setState((prev) => ({
      ...prev,
      books: prev.books.map((book) =>
        book.openlibrary_work_key === openlibraryWorkKey
          ? { ...book, status }
          : book
      ),
    }));
  };

  const renderContent = () => {
    if (state.isLoading) {
      return <LoadingState />;
    }

    if (state.error) {
      return (
        <div
          className="flex flex-col items-center justify-center min-h-[400px] text-center px-4"
          data-testid="error-state"
        >
          <div className="bg-red-100 rounded-full p-6 mb-4">
            <span className="material-icons-round text-red-500 text-5xl">
              error_outline
            </span>
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Something went wrong
          </h2>
          <p className="text-text-sub-light max-w-sm">{state.error}</p>
          <button
            type="button"
            onClick={() => performSearch(debouncedQuery, state.page)}
            className="mt-4 px-4 py-2 bg-primary text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            Try again
          </button>
        </div>
      );
    }

    if (!state.hasSearched) {
      return <EmptyState />;
    }

    if (state.books.length === 0) {
      return <NoResults query={debouncedQuery} />;
    }

    return (
      <>
        <BookGrid books={state.books} onStatusChange={handleStatusChange} />
        <Pagination
          currentPage={state.page}
          totalPages={state.totalPages}
          onPageChange={handlePageChange}
          disabled={state.isLoading}
        />
        {state.totalPages > 0 && (
          <div className="mt-8 text-center">
            <p className="text-text-sub-light text-sm">
              {state.page === state.totalPages
                ? 'End of results'
                : `Page ${state.page} of ${state.totalPages}`}
            </p>
          </div>
        )}
      </>
    );
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <div className="w-full max-w-7xl mx-auto px-6 pt-8 pb-4">
        <div className="mb-6">
          <h1 className="text-4xl font-bold tracking-tight text-gray-900 mb-1">
            Discover
          </h1>
          <p className="text-text-sub-light text-lg font-normal">
            Find your next read
          </p>
        </div>

        {/* Search Bar */}
        <div className="mb-8">
          <SearchBar
            value={query}
            onChange={handleQueryChange}
            onClear={handleClear}
            placeholder="Search by title or author..."
          />
        </div>

        {/* Results Header */}
        {state.hasSearched && state.books.length > 0 && (
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-sm font-semibold tracking-wider text-text-sub-light uppercase">
              Top Results
            </h2>
            <span className="bg-blue-100 text-primary px-3 py-1 rounded-full text-xs font-semibold">
              {state.total} {state.total === 1 ? 'Book' : 'Books'}
            </span>
          </div>
        )}
      </div>

      {/* Main Content */}
      <main className="flex-grow w-full max-w-7xl mx-auto px-6 pb-12">
        {renderContent()}
      </main>

      {/* Footer */}
      <footer className="w-full bg-white border-t border-gray-200 mt-auto py-2">
        <div className="max-w-md mx-auto flex justify-center items-center h-16">
          <div className="flex flex-col items-center justify-center text-primary">
            <span className="material-icons-round text-3xl mb-1">search</span>
            <span className="text-[10px] font-bold tracking-wide">Discover</span>
            <span className="absolute -top-[1px] w-8 h-1 bg-primary rounded-b-lg" />
          </div>
        </div>
      </footer>
    </div>
  );
}
