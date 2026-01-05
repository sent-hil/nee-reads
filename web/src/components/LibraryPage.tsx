/**
 * LibraryPage component showing user's book collection filtered by status
 */

import { useState, useEffect, useCallback, useRef } from 'preact/hooks';
import type { Book, ReadingStatus, StatusCounts } from '../types/book';
import { getLibraryBooks, getStatusCounts, ApiError, setBookStatus, deleteBookStatus } from '../services/api';
import { BookGrid } from './BookGrid';
import { TabBar } from './TabBar';
import { LoadingState } from './LoadingState';
import { LibraryEmptyState } from './LibraryEmptyState';
import { Toast, ToastData } from './Toast';
import { StatusChangeInfo } from './BookCard';

interface LibraryPageProps {
  initialStatus: ReadingStatus;
  onStatusChange: (status: ReadingStatus) => void;
}

const DEFAULT_COUNTS: StatusCounts = {
  to_read: 0,
  did_not_finish: 0,
  completed: 0,
};

export function LibraryPage({ initialStatus, onStatusChange }: LibraryPageProps) {
  const [activeTab, setActiveTab] = useState<ReadingStatus>(initialStatus);
  const [books, setBooks] = useState<Book[]>([]);
  const [counts, setCounts] = useState<StatusCounts>(DEFAULT_COUNTS);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [toast, setToast] = useState<ToastData | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Load books for the active tab
  const loadBooks = useCallback(async (status: ReadingStatus) => {
    // Cancel any pending request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    const abortController = new AbortController();
    abortControllerRef.current = abortController;

    setIsLoading(true);
    setError(null);

    try {
      const [libraryResponse, countsResponse] = await Promise.all([
        getLibraryBooks(status, abortController.signal),
        getStatusCounts(abortController.signal),
      ]);

      // Convert LibraryBook to Book (they have the same shape, just status is required vs optional)
      const booksWithStatus: Book[] = libraryResponse.books.map((book) => ({
        ...book,
        status: book.status,
      }));

      setBooks(booksWithStatus);
      setCounts(countsResponse);
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') {
        return;
      }
      const message =
        err instanceof ApiError
          ? err.message
          : 'Failed to load library. Please try again.';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Load books when active tab changes
  useEffect(() => {
    loadBooks(activeTab);
  }, [activeTab, loadBooks]);

  // Update activeTab when initialStatus prop changes (from URL navigation)
  useEffect(() => {
    setActiveTab(initialStatus);
  }, [initialStatus]);

  const handleTabChange = (tab: ReadingStatus) => {
    setActiveTab(tab);
    onStatusChange(tab);
  };

  const handleStatusChange = (info: StatusChangeInfo) => {
    // If the new status is different from the current tab, remove the book from view
    if (info.newStatus !== activeTab) {
      setBooks((prev) =>
        prev.filter((book) => book.openlibrary_work_key !== info.openlibraryWorkKey)
      );

      // Update counts
      setCounts((prev) => ({
        ...prev,
        [activeTab]: Math.max(0, prev[activeTab] - 1),
        [info.newStatus]: prev[info.newStatus] + 1,
      }));
    }

    // Show toast notification
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
        // If there was no previous status, delete it
        await deleteBookStatus(toastData.openlibraryWorkKey);
      } else {
        // Find the book in current list or use metadata from the books list
        const book = books.find(
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

      // Reload the current tab to get fresh data
      await loadBooks(activeTab);
    } catch (error) {
      console.error('Failed to undo status change:', error);
    }
  };

  const renderContent = () => {
    if (isLoading) {
      return <LoadingState />;
    }

    if (error) {
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
          <p className="text-text-sub-light max-w-sm">{error}</p>
          <button
            type="button"
            onClick={() => loadBooks(activeTab)}
            className="mt-4 px-4 py-2 bg-primary text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            Try again
          </button>
        </div>
      );
    }

    if (books.length === 0) {
      return <LibraryEmptyState status={activeTab} />;
    }

    return (
      <>
        <BookGrid books={books} onStatusChange={handleStatusChange} />
        <div className="mt-12 text-center">
          <p className="text-text-sub-light text-sm">
            Showing {books.length} of {counts[activeTab]} books
          </p>
        </div>
      </>
    );
  };

  return (
    <>
      {/* Header */}
      <div className="w-full max-w-7xl mx-auto px-6 pt-8 pb-4">
        <div className="mb-6">
          <h1 className="text-4xl font-bold tracking-tight text-gray-900 mb-1">
            Library
          </h1>
          <p className="text-text-sub-light text-lg font-normal">
            Your collection
          </p>
        </div>

        {/* Tab Bar */}
        <TabBar activeTab={activeTab} counts={counts} onTabChange={handleTabChange} />
      </div>

      {/* Main Content */}
      <main className="flex-grow w-full max-w-7xl mx-auto px-6 pb-28">
        {renderContent()}
      </main>

      {/* Toast notification */}
      {toast && (
        <Toast toast={toast} onUndo={handleUndo} onDismiss={handleToastDismiss} />
      )}
    </>
  );
}
