/**
 * NoResults component shown when search returns no results
 */

interface NoResultsProps {
  query: string;
}

export function NoResults({ query }: NoResultsProps) {
  return (
    <div
      className="flex flex-col items-center justify-center min-h-[400px] text-center px-4"
      data-testid="no-results"
    >
      <div className="bg-gray-100 rounded-full p-6 mb-4">
        <span className="material-icons-round text-gray-400 text-5xl">
          search_off
        </span>
      </div>
      <h2 className="text-xl font-semibold text-gray-900 mb-2">
        No results found
      </h2>
      <p className="text-text-sub-light max-w-sm">
        We couldn't find any books matching "{query}". Try a different search term.
      </p>
    </div>
  );
}
