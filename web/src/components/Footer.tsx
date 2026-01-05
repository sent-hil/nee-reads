/**
 * Footer navigation component with Library and Discover tabs
 */

export type Page = 'discover' | 'library';

interface FooterProps {
  activePage: Page;
  onNavigate: (page: Page) => void;
}

export function Footer({ activePage, onNavigate }: FooterProps) {
  return (
    <footer className="w-full bg-white border-t border-gray-200 fixed bottom-0 left-0 right-0 z-40">
      <div className="max-w-md mx-auto flex justify-around items-center h-16">
        <button
          onClick={() => onNavigate('library')}
          className={`flex flex-col items-center justify-center w-full h-full transition-colors group relative ${
            activePage === 'library'
              ? 'text-primary'
              : 'text-gray-400 hover:text-primary'
          }`}
        >
          <span
            className={`material-icons-round mb-1 group-hover:scale-110 transition-transform ${
              activePage === 'library' ? 'text-3xl' : 'text-2xl'
            }`}
          >
            library_books
          </span>
          <span
            className={`text-[10px] tracking-wide ${
              activePage === 'library' ? 'font-bold' : 'font-medium'
            }`}
          >
            Library
          </span>
          {activePage === 'library' && (
            <span className="absolute -top-[1px] w-8 h-1 bg-primary rounded-b-lg" />
          )}
        </button>

        <button
          onClick={() => onNavigate('discover')}
          className={`flex flex-col items-center justify-center w-full h-full transition-colors group relative ${
            activePage === 'discover'
              ? 'text-primary'
              : 'text-gray-400 hover:text-primary'
          }`}
        >
          <span
            className={`material-icons-round mb-1 group-hover:scale-110 transition-transform ${
              activePage === 'discover' ? 'text-3xl' : 'text-2xl'
            }`}
          >
            search
          </span>
          <span
            className={`text-[10px] tracking-wide ${
              activePage === 'discover' ? 'font-bold' : 'font-medium'
            }`}
          >
            Discover
          </span>
          {activePage === 'discover' && (
            <span className="absolute -top-[1px] w-8 h-1 bg-primary rounded-b-lg" />
          )}
        </button>
      </div>
    </footer>
  );
}
