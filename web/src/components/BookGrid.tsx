/**
 * BookGrid component displaying a responsive grid of book cards
 */

import type { Book } from '../types/book';
import { BookCard } from './BookCard';

interface BookGridProps {
  books: Book[];
}

export function BookGrid({ books }: BookGridProps) {
  if (books.length === 0) {
    return null;
  }

  return (
    <div
      className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6"
      data-testid="book-grid"
    >
      {books.map((book) => (
        <BookCard key={book.openlibrary_work_key} book={book} />
      ))}
    </div>
  );
}
