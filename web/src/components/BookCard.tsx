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
      data-book-key={book.key}
    >
      <div className="aspect-[2/3] w-full bg-white rounded-xl shadow-md overflow-hidden transition-transform duration-300 book-card-hover cursor-pointer relative">
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
