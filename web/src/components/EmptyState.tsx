/**
 * EmptyState component shown before any search is performed
 */

export function EmptyState() {
  return (
    <div
      className="flex flex-col items-center justify-center min-h-[400px] text-center px-4"
      data-testid="empty-state"
    >
      <div className="bg-blue-100 rounded-full p-6 mb-4">
        <span className="material-icons-round text-primary text-5xl">
          auto_stories
        </span>
      </div>
      <h2 className="text-xl font-semibold text-gray-900 mb-2">
        Search for books
      </h2>
      <p className="text-text-sub-light max-w-sm">
        Enter a book title or author name to discover your next great read
      </p>
    </div>
  );
}
