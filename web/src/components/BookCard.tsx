/**
 * BookCard component displaying a single book with cover, title, and author
 */

import type { Book } from '../types/book';

interface BookCardProps {
  book: Book;
}

export function BookCard({ book }: BookCardProps) {
  const authorDisplay =
    book.author_name.length > 0 ? book.author_name.join(', ') : 'Unknown Author';

  return (
    <div
      className="group relative flex flex-col"
      data-testid="book-card"
      data-book-key={book.openlibrary_work_key}
    >
      <div className="aspect-[2/3] w-full bg-white rounded-xl shadow-md overflow-hidden transition-transform duration-300 book-card-hover cursor-pointer relative z-0">
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
      {/* Dropdown menu */}
      <div className="absolute top-2 right-2 z-10">
        <div className="relative">
          <button
            className={`flex items-center justify-center w-8 h-8 rounded-full shadow-sm opacity-0 group-hover:opacity-100 focus:opacity-100 transition-all duration-200 focus:outline-none peer ${
              book.cover_url
                ? 'bg-black/40 hover:bg-black/60 backdrop-blur-md text-white'
                : 'bg-gray-200/50 hover:bg-gray-200 text-gray-600'
            }`}
            aria-label="Book options"
          >
            <span className="material-icons-round text-lg">more_vert</span>
          </button>
          <div className="hidden peer-focus:block hover:block absolute right-0 mt-2 w-36 bg-white rounded-xl shadow-floating border border-gray-100 py-1.5 text-left z-20 origin-top-right">
            <button
              onClick={() => {}}
              className="block w-full px-4 py-2 text-xs font-medium text-text-main-light hover:bg-gray-50 transition-colors text-left"
            >
              To Read
            </button>
            <button
              onClick={() => {}}
              className="block w-full px-4 py-2 text-xs font-medium text-text-main-light hover:bg-gray-50 transition-colors text-left"
            >
              Didn't Finish
            </button>
            <button
              onClick={() => {}}
              className="block w-full px-4 py-2 text-xs font-medium text-text-main-light hover:bg-gray-50 transition-colors text-left"
            >
              Completed
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
