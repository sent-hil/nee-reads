/**
 * LoadingState component showing skeleton cards while loading
 */

interface LoadingStateProps {
  count?: number;
}

export function LoadingState({ count = 10 }: LoadingStateProps) {
  return (
    <div
      className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6"
      data-testid="loading-state"
    >
      {Array.from({ length: count }).map((_, index) => (
        <div key={index} className="flex flex-col animate-pulse">
          <div className="aspect-[2/3] w-full bg-gray-200 rounded-xl" />
          <div className="mt-3 space-y-2">
            <div className="h-4 bg-gray-200 rounded w-3/4" />
            <div className="h-3 bg-gray-200 rounded w-1/2" />
          </div>
        </div>
      ))}
    </div>
  );
}
