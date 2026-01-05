/**
 * LibraryEmptyState component shown when there are no books in a library category
 */

import type { ReadingStatus } from '../types/book';

interface LibraryEmptyStateProps {
  status: ReadingStatus;
}

const STATUS_LABELS: Record<ReadingStatus, string> = {
  to_read: 'To Read',
  did_not_finish: "Didn't Finish",
  completed: 'Completed',
};

const STATUS_MESSAGES: Record<ReadingStatus, string> = {
  to_read: 'Books you want to read will appear here',
  did_not_finish: "Books you didn't finish will appear here",
  completed: 'Books you have completed will appear here',
};

export function LibraryEmptyState({ status }: LibraryEmptyStateProps) {
  return (
    <div
      className="flex flex-col items-center justify-center min-h-[400px] text-center px-4"
      data-testid="library-empty-state"
    >
      <div className="bg-blue-100 rounded-full p-6 mb-4">
        <span className="material-icons-round text-primary text-5xl">
          library_books
        </span>
      </div>
      <h2 className="text-xl font-semibold text-gray-900 mb-2">
        No books in {STATUS_LABELS[status]}
      </h2>
      <p className="text-text-sub-light max-w-sm">
        {STATUS_MESSAGES[status]}. Search for books and add them to your library.
      </p>
    </div>
  );
}
