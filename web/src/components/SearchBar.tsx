/**
 * SearchBar component with search icon and clear button
 */

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  onClear: () => void;
  placeholder?: string;
  disabled?: boolean;
}

export function SearchBar({
  value,
  onChange,
  onClear,
  placeholder = 'Search for books...',
  disabled = false,
}: SearchBarProps) {
  const handleInputChange = (e: Event) => {
    const target = e.target as HTMLInputElement;
    onChange(target.value);
  };

  const handleClearClick = () => {
    onClear();
  };

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'Escape') {
      onClear();
    }
  };

  return (
    <div className="relative w-full group" data-testid="search-bar">
      <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
        <span className="material-icons-round text-primary text-2xl group-focus-within:text-blue-600 transition-colors">
          search
        </span>
      </div>
      <input
        type="text"
        value={value}
        onInput={handleInputChange}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={disabled}
        className="block w-full pl-12 pr-12 py-4 bg-white border-none rounded-2xl text-lg text-gray-900 placeholder-gray-400 focus:ring-2 focus:ring-primary shadow-soft transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        data-testid="search-input"
        aria-label="Search for books"
      />
      {value && (
        <div className="absolute inset-y-0 right-0 pr-4 flex items-center">
          <button
            type="button"
            onClick={handleClearClick}
            className="text-gray-400 hover:text-gray-600 transition-colors focus:outline-none focus:text-gray-600"
            data-testid="clear-button"
            aria-label="Clear search"
          >
            <span className="material-icons-round">cancel</span>
          </button>
        </div>
      )}
    </div>
  );
}
