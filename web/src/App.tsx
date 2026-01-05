/**
 * Main App component with routing
 */

import { useState, useEffect, useCallback, useRef } from 'preact/hooks';
import type { Book, ReadingStatus } from './types/book';
import { searchBooks, ApiError, setBookStatus, deleteBookStatus } from './services/api';
import { useDebounce } from './hooks/useDebounce';
import { SearchBar } from './components/SearchBar';
import { BookGrid } from './components/BookGrid';
import { Pagination } from './components/Pagination';
import { EmptyState } from './components/EmptyState';
import { NoResults } from './components/NoResults';
import { LoadingState } from './components/LoadingState';
import { Toast, ToastData } from './components/Toast';
import { StatusChangeInfo } from './components/BookCard';
import { Footer, Page } from './components/Footer';
import { LibraryPage } from './components/LibraryPage';

const DEBOUNCE_DELAY = 500;

// Routing helpers

type Route =
  | { page: 'discover'; query: string }
  | { page: 'library'; status: ReadingStatus };

/** Map URL slug to ReadingStatus */
const SLUG_TO_STATUS: Record<string, ReadingStatus> = {
  'to-read': 'to_read',
  'did-not-finish': 'did_not_finish',
  'completed': 'completed',
};

/** Map ReadingStatus to URL slug */
const STATUS_TO_SLUG: Record<ReadingStatus, string> = {
  to_read: 'to-read',
  did_not_finish: 'did-not-finish',
  completed: 'completed',
};

/** Parse the current URL to determine the route */
function getRouteFromUrl(): Route {
  const path = window.location.pathname;
  const params = new URLSearchParams(window.location.search);

  // Check for library routes
  if (path.startsWith('/library/')) {
    const slug = path.replace('/library/', '');
    const status = SLUG_TO_STATUS[slug];
    if (status) {
      return { page: 'library', status };
    }
  }

  // Default to discover page
  return { page: 'discover', query: params.get('q') || '' };
}

/** Navigate to a new route */
function navigateTo(route: Route): void {
  let url: string;
  if (route.page === 'library') {
    url = `/library/${STATUS_TO_SLUG[route.status]}`;
  } else {
    url = route.query ? `/?q=${encodeURIComponent(route.query)}` : '/';
  }
  window.history.pushState({}, '', url);
}

// Discover page state
interface SearchState {
  books: Book[];
  total: number;
  page: number;
  totalPages: number;
  isLoading: boolean;
  error: string | null;
  hasSearched: boolean;
}

const initialSearchState: SearchState = {
  books: [],
  total: 0,
  page: 1,
  totalPages: 0,
  isLoading: false,
  error: null,
  hasSearched: false,
};

export function App() {
  const [route, setRoute] = useState<Route>(getRouteFromUrl);
  const [query, setQuery] = useState(route.page === 'discover' ? route.query : '');
  const [state, setState] = useState<SearchState>(initialSearchState);
  const [toast, setToast] = useState<ToastData | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const isInitialMount = useRef(true);

  const debouncedQuery = useDebounce(query.trim(), DEBOUNCE_DELAY);

  // Handle browser back/forward navigation
  useEffect(() => {
    const handlePopState = () => {
      const newRoute = getRouteFromUrl();
      setRoute(newRoute);
      if (newRoute.page === 'discover') {
        setQuery(newRoute.query);
      }
    };
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  // Update URL when debounced query changes on discover page
  useEffect(() => {
    if (route.page !== 'discover') return;
    if (isInitialMount.current) {
      isInitialMount.current = false;
      return;
    }
    navigateTo({ page: 'discover', query: debouncedQuery });
  }, [debouncedQuery, route.page]);

  const performSearch = useCallback(
    async (searchQuery: string, page: number) => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }

      if (!searchQuery) {
        setState(initialSearchState);
        return;
      }

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
    if (route.page === 'discover') {
      performSearch(debouncedQuery, 1);
    }
  }, [debouncedQuery, performSearch, route.page]);

  const handleQueryChange = (newQuery: string) => {
    setQuery(newQuery);
  };

  const handleClear = () => {
    setQuery('');
    setState(initialSearchState);
    navigateTo({ page: 'discover', query: '' });
  };

  const handlePageChange = (newPage: number) => {
    performSearch(debouncedQuery, newPage);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleStatusChange = (info: StatusChangeInfo) => {
    setState((prev) => ({
      ...prev,
      books: prev.books.map((book) =>
        book.openlibrary_work_key === info.openlibraryWorkKey
          ? { ...book, status: info.newStatus }
          : book
      ),
    }));

    setToast({
      id: `${info.openlibraryWorkKey}-${Date.now()}`,
      bookTitle: info.bookTitle,
      status: info.newStatus,
      openlibraryWorkKey: info.openlibraryWorkKey,
      previousStatus: info.previousStatus,
    });
  };

  const handleToastDismiss = () => {
    setToast(null);
  };

  const handleUndo = async (toastData: ToastData) => {
    setToast(null);

    try {
      if (toastData.previousStatus === null) {
        await deleteBookStatus(toastData.openlibraryWorkKey);
      } else {
        // Find the book to get metadata
        const book = state.books.find(
          (b) => b.openlibrary_work_key === toastData.openlibraryWorkKey
        );
        if (book) {
          await setBookStatus(toastData.openlibraryWorkKey, toastData.previousStatus, {
            title: book.title,
            author_name: book.author_name,
            cover_url: book.cover_url,
            first_publish_year: book.first_publish_year,
          });
        }
      }

      setState((prev) => ({
        ...prev,
        books: prev.books.map((book) =>
          book.openlibrary_work_key === toastData.openlibraryWorkKey
            ? { ...book, status: toastData.previousStatus }
            : book
        ),
      }));
    } catch (error) {
      console.error('Failed to undo status change:', error);
    }
  };

  const handleNavigate = (page: Page) => {
    if (page === 'library') {
      const newRoute: Route = { page: 'library', status: 'to_read' };
      setRoute(newRoute);
      navigateTo(newRoute);
    } else {
      const newRoute: Route = { page: 'discover', query };
      setRoute(newRoute);
      navigateTo(newRoute);
    }
  };

  const handleLibraryStatusChange = (status: ReadingStatus) => {
    const newRoute: Route = { page: 'library', status };
    setRoute(newRoute);
    navigateTo(newRoute);
  };

  const renderDiscoverContent = () => {
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

  const renderDiscoverPage = () => (
    <>
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
      <main className="flex-grow w-full max-w-7xl mx-auto px-6 pb-28">
        {renderDiscoverContent()}
      </main>

      {/* Toast notification */}
      {toast && (
        <Toast toast={toast} onUndo={handleUndo} onDismiss={handleToastDismiss} />
      )}
    </>
  );

  return (
    <div className="min-h-screen flex flex-col">
      {route.page === 'discover' ? (
        renderDiscoverPage()
      ) : (
        <LibraryPage
          initialStatus={route.status}
          onStatusChange={handleLibraryStatusChange}
        />
      )}

      {/* Footer Navigation */}
      <Footer activePage={route.page} onNavigate={handleNavigate} />
    </div>
  );
}
