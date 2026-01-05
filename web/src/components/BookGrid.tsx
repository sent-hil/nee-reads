/**
 * BookGrid component displaying a responsive grid of book cards
 */

import type { Book, ReadingStatus } from '../types/book';
import { BookCard } from './BookCard';

interface BookGridProps {
  books: Book[];
  onStatusChange?: (openlibraryWorkKey: string, status: ReadingStatus) => void;
}

export function BookGrid({ books, onStatusChange }: BookGridProps) {
  if (books.length === 0) {
    return null;
  }

  return (
    <div
      className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6"
      data-testid="book-grid"
    >
      {books.map((book) => (
        <BookCard
          key={book.openlibrary_work_key}
          book={book}
          onStatusChange={onStatusChange}
        />
      ))}
    </div>
  );
}
