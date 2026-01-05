/**
 * BookCard component displaying a single book with cover, title, and author
 */

import { useState, useRef } from 'preact/hooks';
import type { Book, ReadingStatus, BookMetadata } from '../types/book';
import { setBookStatus } from '../services/api';

export interface StatusChangeInfo {
  openlibraryWorkKey: string;
  bookTitle: string;
  newStatus: ReadingStatus;
  previousStatus: ReadingStatus | null;
  bookMetadata: BookMetadata;
}

interface BookCardProps {
  book: Book;
  onStatusChange?: (info: StatusChangeInfo) => void;
}

const STATUS_LABELS: Record<ReadingStatus, string> = {
  to_read: 'To Read',
  did_not_finish: "Didn't Finish",
  completed: 'Completed',
};

export function BookCard({ book, onStatusChange }: BookCardProps) {
  const [isUpdating, setIsUpdating] = useState(false);
  // Initialize from book.status (from API) - this reflects database state
  const [localStatus, setLocalStatus] = useState<ReadingStatus | null>(book.status);
  const menuButtonRef = useRef<HTMLButtonElement>(null);

  const authorDisplay =
    book.author_name.length > 0 ? book.author_name.join(', ') : 'Unknown Author';

  const bookMetadata: BookMetadata = {
    title: book.title,
    author_name: book.author_name,
    cover_url: book.cover_url,
    first_publish_year: book.first_publish_year,
  };

  const handleStatusClick = async (status: ReadingStatus) => {
    if (isUpdating) return;

    const previousStatus = localStatus;

    // Close dropdown immediately by blurring the button
    menuButtonRef.current?.blur();

    setIsUpdating(true);
    try {
      await setBookStatus(book.openlibrary_work_key, status, bookMetadata);
      setLocalStatus(status);
      onStatusChange?.({
        openlibraryWorkKey: book.openlibrary_work_key,
        bookTitle: book.title,
        newStatus: status,
        previousStatus,
        bookMetadata,
      });
    } catch (error) {
      console.error('Failed to update book status:', error);
    } finally {
      setIsUpdating(false);
    }
  };

  const isSelected = (status: ReadingStatus) => localStatus === status;

  return (
    <div
      className="group relative flex flex-col"
      data-testid="book-card"
      data-book-key={book.openlibrary_work_key}
    >
      <div className="aspect-[2/3] w-full bg-white rounded-xl shadow-md overflow-hidden transition-transform duration-300 book-card-hover cursor-pointer relative z-0">
        {/* Status badge - top left */}
        {localStatus && (
          <div className="absolute top-3 left-3 z-20">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[10px] font-bold bg-white/90 backdrop-blur-md text-primary shadow-sm ring-1 ring-black/5">
              <span className="w-1.5 h-1.5 rounded-full bg-primary"></span>
              {STATUS_LABELS[localStatus]}
            </span>
          </div>
        )}

        {book.cover_url ? (
          <img
            src={book.cover_url}
            alt={`Cover of ${book.title}`}
            className="object-cover w-full h-full opacity-90 group-hover:opacity-100 transition-opacity"
            loading="lazy"
            onError={(e) => {
              // Hide broken image and show placeholder
              const target = e.target as HTMLImageElement;
              target.style.display = 'none';
              const placeholder = target.nextElementSibling;
              if (placeholder) {
                (placeholder as HTMLElement).style.display = 'flex';
              }
            }}
          />
        ) : null}
        <div
          className={`${book.cover_url ? 'hidden' : 'flex'} absolute inset-0 bg-gray-50 flex-col items-center justify-center text-center p-4`}
          data-testid="cover-placeholder"
        >
          <span className="material-icons-round text-4xl text-gray-400 mb-2">
            menu_book
          </span>
          <span className="text-xs font-medium text-gray-500">
            Cover
            <br />
            Unavailable
          </span>
        </div>
      </div>

      {/* Dropdown menu - top right */}
      <div className="absolute top-2 right-2 z-10">
        <div className="relative">
          <button
            ref={menuButtonRef}
            className={`flex items-center justify-center w-8 h-8 rounded-full shadow-sm opacity-0 group-hover:opacity-100 focus:opacity-100 transition-all duration-200 focus:outline-none peer ${
              book.cover_url
                ? 'bg-black/40 hover:bg-black/60 backdrop-blur-md text-white'
                : 'bg-gray-200/50 hover:bg-gray-200 text-gray-600'
            } ${isUpdating ? 'cursor-wait' : ''}`}
            aria-label="Book options"
            disabled={isUpdating}
          >
            <span className="material-icons-round text-lg">
              {isUpdating ? 'hourglass_empty' : 'more_vert'}
            </span>
          </button>
          <div className="hidden peer-focus:block hover:block absolute right-0 mt-2 w-40 bg-white rounded-xl shadow-floating border border-gray-100 p-1 text-left z-20 origin-top-right">
            <button
              onClick={() => handleStatusClick('to_read')}
              className={`flex items-center justify-between w-full px-3 py-2 text-xs font-medium rounded-lg transition-colors ${
                isSelected('to_read')
                  ? 'text-primary bg-blue-50 font-semibold'
                  : 'text-text-main-light hover:bg-gray-50'
              }`}
              disabled={isUpdating}
            >
              <span>To Read</span>
              {isSelected('to_read') && (
                <span className="material-icons-round text-[14px]">check</span>
              )}
            </button>
            <button
              onClick={() => handleStatusClick('did_not_finish')}
              className={`flex items-center justify-between w-full px-3 py-2 text-xs font-medium rounded-lg transition-colors ${
                isSelected('did_not_finish')
                  ? 'text-primary bg-blue-50 font-semibold'
                  : 'text-text-main-light hover:bg-gray-50'
              }`}
              disabled={isUpdating}
            >
              <span>Didn't Finish</span>
              {isSelected('did_not_finish') && (
                <span className="material-icons-round text-[14px]">check</span>
              )}
            </button>
            <button
              onClick={() => handleStatusClick('completed')}
              className={`flex items-center justify-between w-full px-3 py-2 text-xs font-medium rounded-lg transition-colors ${
                isSelected('completed')
                  ? 'text-primary bg-blue-50 font-semibold'
                  : 'text-text-main-light hover:bg-gray-50'
              }`}
              disabled={isUpdating}
            >
              <span>Completed</span>
              {isSelected('completed') && (
                <span className="material-icons-round text-[14px]">check</span>
              )}
            </button>
          </div>
        </div>
      </div>

      <div className="mt-3">
        <h3
          className="text-base font-semibold text-gray-900 leading-tight truncate"
          title={book.title}
          data-testid="book-title"
        >
          {book.title}
        </h3>
        <p
          className="text-sm text-text-sub-light truncate"
          title={authorDisplay}
          data-testid="book-author"
        >
          {authorDisplay}
        </p>
      </div>
    </div>
  );
}
