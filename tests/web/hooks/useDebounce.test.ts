/**
 * Tests for useDebounce hook
 */

import { renderHook, act } from '@testing-library/preact';
import { useDebounce } from '../../../web/src/hooks/useDebounce';

describe('useDebounce', () => {
  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('returns initial value immediately', () => {
    const { result } = renderHook(() => useDebounce('initial', 500));
    expect(result.current).toBe('initial');
  });

  it('does not update value before delay', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 'initial', delay: 500 } }
    );

    rerender({ value: 'updated', delay: 500 });

    // Value should still be initial before delay
    expect(result.current).toBe('initial');

    // Advance time but not enough
    act(() => {
      jest.advanceTimersByTime(300);
    });

    expect(result.current).toBe('initial');
  });

  it('updates value after delay', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 'initial', delay: 500 } }
    );

    rerender({ value: 'updated', delay: 500 });

    act(() => {
      jest.advanceTimersByTime(500);
    });

    expect(result.current).toBe('updated');
  });

  it('resets timer on rapid value changes', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 'initial', delay: 500 } }
    );

    // First change
    rerender({ value: 'change1', delay: 500 });

    act(() => {
      jest.advanceTimersByTime(300);
    });

    // Second change before first timer completes
    rerender({ value: 'change2', delay: 500 });

    act(() => {
      jest.advanceTimersByTime(300);
    });

    // Should still be initial (timer reset)
    expect(result.current).toBe('initial');

    // Third change
    rerender({ value: 'change3', delay: 500 });

    // Complete the full delay
    act(() => {
      jest.advanceTimersByTime(500);
    });

    // Should be the final value
    expect(result.current).toBe('change3');
  });

  it('works with different delay values', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 'initial', delay: 1000 } }
    );

    rerender({ value: 'updated', delay: 1000 });

    act(() => {
      jest.advanceTimersByTime(500);
    });

    expect(result.current).toBe('initial');

    act(() => {
      jest.advanceTimersByTime(500);
    });

    expect(result.current).toBe('updated');
  });

  it('handles zero delay', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 'initial', delay: 0 } }
    );

    rerender({ value: 'updated', delay: 0 });

    act(() => {
      jest.advanceTimersByTime(0);
    });

    expect(result.current).toBe('updated');
  });

  it('works with non-string values', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 42, delay: 500 } }
    );

    rerender({ value: 100, delay: 500 });

    act(() => {
      jest.advanceTimersByTime(500);
    });

    expect(result.current).toBe(100);
  });

  it('works with objects', () => {
    const initial = { name: 'initial' };
    const updated = { name: 'updated' };

    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: initial, delay: 500 } }
    );

    rerender({ value: updated, delay: 500 });

    act(() => {
      jest.advanceTimersByTime(500);
    });

    expect(result.current).toEqual(updated);
  });

  it('cleans up timer on unmount', () => {
    const { unmount, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 'initial', delay: 500 } }
    );

    rerender({ value: 'updated', delay: 500 });

    // Unmount before timer completes
    unmount();

    // This should not throw
    act(() => {
      jest.advanceTimersByTime(500);
    });
  });
});
