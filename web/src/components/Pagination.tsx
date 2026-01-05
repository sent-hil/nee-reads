/**
 * Pagination component with numbered page buttons
 */

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  disabled?: boolean;
}

export function Pagination({
  currentPage,
  totalPages,
  onPageChange,
  disabled = false,
}: PaginationProps) {
  if (totalPages <= 1) {
    return null;
  }

  // Generate page numbers to display
  const getPageNumbers = (): (number | string)[] => {
    const pages: (number | string)[] = [];
    const maxVisiblePages = 5;

    if (totalPages <= maxVisiblePages) {
      // Show all pages if total is small
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      // Always show first page
      pages.push(1);

      if (currentPage > 3) {
        pages.push('...');
      }

      // Show pages around current page
      const start = Math.max(2, currentPage - 1);
      const end = Math.min(totalPages - 1, currentPage + 1);

      for (let i = start; i <= end; i++) {
        pages.push(i);
      }

      if (currentPage < totalPages - 2) {
        pages.push('...');
      }

      // Always show last page
      pages.push(totalPages);
    }

    return pages;
  };

  const handlePrevious = () => {
    if (currentPage > 1 && !disabled) {
      onPageChange(currentPage - 1);
    }
  };

  const handleNext = () => {
    if (currentPage < totalPages && !disabled) {
      onPageChange(currentPage + 1);
    }
  };

  const handlePageClick = (page: number) => {
    if (!disabled && page !== currentPage) {
      onPageChange(page);
    }
  };

  const baseButtonClass =
    'px-3 py-2 text-sm font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2';
  const activeClass = 'bg-primary text-white';
  const inactiveClass = 'bg-white text-gray-700 hover:bg-gray-100';
  const disabledClass = 'opacity-50 cursor-not-allowed';

  return (
    <nav
      className="flex items-center justify-center gap-1 mt-8"
      data-testid="pagination"
      aria-label="Pagination"
    >
      <button
        type="button"
        onClick={handlePrevious}
        disabled={disabled || currentPage === 1}
        className={`${baseButtonClass} ${inactiveClass} ${disabled || currentPage === 1 ? disabledClass : ''}`}
        data-testid="pagination-prev"
        aria-label="Previous page"
      >
        <span className="material-icons-round text-lg">chevron_left</span>
      </button>

      {getPageNumbers().map((page, index) =>
        typeof page === 'string' ? (
          <span
            key={`ellipsis-${index}`}
            className="px-3 py-2 text-sm text-gray-500"
            data-testid="pagination-ellipsis"
          >
            {page}
          </span>
        ) : (
          <button
            key={page}
            type="button"
            onClick={() => handlePageClick(page)}
            disabled={disabled}
            className={`${baseButtonClass} ${page === currentPage ? activeClass : inactiveClass} ${disabled ? disabledClass : ''}`}
            data-testid={`pagination-page-${page}`}
            aria-label={`Page ${page}`}
            aria-current={page === currentPage ? 'page' : undefined}
          >
            {page}
          </button>
        )
      )}

      <button
        type="button"
        onClick={handleNext}
        disabled={disabled || currentPage === totalPages}
        className={`${baseButtonClass} ${inactiveClass} ${disabled || currentPage === totalPages ? disabledClass : ''}`}
        data-testid="pagination-next"
        aria-label="Next page"
      >
        <span className="material-icons-round text-lg">chevron_right</span>
      </button>
    </nav>
  );
}
