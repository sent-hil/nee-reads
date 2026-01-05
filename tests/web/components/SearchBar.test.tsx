/**
 * Tests for SearchBar component
 */

import { render, screen, fireEvent } from '@testing-library/preact';
import { SearchBar } from '../../../web/src/components/SearchBar';

describe('SearchBar', () => {
  const defaultProps = {
    value: '',
    onChange: jest.fn(),
    onClear: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('rendering', () => {
    it('renders search input', () => {
      render(<SearchBar {...defaultProps} />);
      expect(screen.getByTestId('search-input')).toBeInTheDocument();
    });

    it('renders search bar container', () => {
      render(<SearchBar {...defaultProps} />);
      expect(screen.getByTestId('search-bar')).toBeInTheDocument();
    });

    it('renders with provided value', () => {
      render(<SearchBar {...defaultProps} value="test query" />);
      expect(screen.getByTestId('search-input')).toHaveValue('test query');
    });

    it('renders with custom placeholder', () => {
      render(<SearchBar {...defaultProps} placeholder="Custom placeholder" />);
      expect(screen.getByPlaceholderText('Custom placeholder')).toBeInTheDocument();
    });

    it('renders default placeholder when not provided', () => {
      render(<SearchBar {...defaultProps} />);
      expect(screen.getByPlaceholderText('Search for books...')).toBeInTheDocument();
    });

    it('disables input when disabled prop is true', () => {
      render(<SearchBar {...defaultProps} disabled={true} />);
      expect(screen.getByTestId('search-input')).toBeDisabled();
    });
  });

  describe('clear button', () => {
    it('does not render clear button when value is empty', () => {
      render(<SearchBar {...defaultProps} value="" />);
      expect(screen.queryByTestId('clear-button')).not.toBeInTheDocument();
    });

    it('renders clear button when value is not empty', () => {
      render(<SearchBar {...defaultProps} value="test" />);
      expect(screen.getByTestId('clear-button')).toBeInTheDocument();
    });

    it('calls onClear when clear button is clicked', () => {
      const onClear = jest.fn();
      render(<SearchBar {...defaultProps} value="test" onClear={onClear} />);
      
      fireEvent.click(screen.getByTestId('clear-button'));
      expect(onClear).toHaveBeenCalledTimes(1);
    });
  });

  describe('input handling', () => {
    it('calls onChange when input value changes', () => {
      const onChange = jest.fn();
      render(<SearchBar {...defaultProps} onChange={onChange} />);
      
      fireEvent.input(screen.getByTestId('search-input'), {
        target: { value: 'new value' },
      });
      
      expect(onChange).toHaveBeenCalledWith('new value');
    });

    it('calls onClear when Escape key is pressed', () => {
      const onClear = jest.fn();
      render(<SearchBar {...defaultProps} value="test" onClear={onClear} />);
      
      fireEvent.keyDown(screen.getByTestId('search-input'), { key: 'Escape' });
      expect(onClear).toHaveBeenCalledTimes(1);
    });

    it('does not call onClear for other keys', () => {
      const onClear = jest.fn();
      render(<SearchBar {...defaultProps} value="test" onClear={onClear} />);
      
      fireEvent.keyDown(screen.getByTestId('search-input'), { key: 'Enter' });
      expect(onClear).not.toHaveBeenCalled();
    });
  });

  describe('accessibility', () => {
    it('has accessible label for input', () => {
      render(<SearchBar {...defaultProps} />);
      expect(screen.getByLabelText('Search for books')).toBeInTheDocument();
    });

    it('has accessible label for clear button', () => {
      render(<SearchBar {...defaultProps} value="test" />);
      expect(screen.getByLabelText('Clear search')).toBeInTheDocument();
    });
  });
});
