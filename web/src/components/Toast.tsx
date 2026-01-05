/**
 * Toast notification component for status change feedback
 */

import { useEffect } from 'preact/hooks';
import type { ReadingStatus } from '../types/book';

const STATUS_LABELS: Record<ReadingStatus, string> = {
  to_read: 'To Read',
  did_not_finish: "Didn't Finish",
  completed: 'Completed',
};

export interface ToastData {
  id: string;
  bookTitle: string;
  status: ReadingStatus;
  openlibraryWorkKey: string;
  previousStatus: ReadingStatus | null;
}

interface ToastProps {
  toast: ToastData;
  onUndo: (toast: ToastData) => void;
  onDismiss: (id: string) => void;
}

const TOAST_DURATION = 5000; // 5 seconds

export function Toast({ toast, onUndo, onDismiss }: ToastProps) {
  useEffect(() => {
    const timer = setTimeout(() => {
      onDismiss(toast.id);
    }, TOAST_DURATION);

    return () => clearTimeout(timer);
  }, [toast.id, onDismiss]);

  const handleUndo = () => {
    onUndo(toast);
  };

  return (
    <div className="fixed bottom-24 left-1/2 z-50 w-max max-w-[90%] toast-animate">
      <div className="flex items-center justify-between gap-4 pl-4 pr-3 py-2.5 bg-gray-900/95 backdrop-blur-md text-white rounded-2xl shadow-floating border border-white/10 ring-1 ring-black/10">
        <div className="flex items-center gap-3">
          <div className="bg-green-500/20 p-1 rounded-full flex items-center justify-center">
            <span className="material-icons-round text-green-400 text-sm leading-none">
              check
            </span>
          </div>
          <p className="text-xs sm:text-sm font-medium">
            Book added to{' '}
            <span className="font-bold text-white">
              {STATUS_LABELS[toast.status]}
            </span>{' '}
            list
          </p>
        </div>
        <button
          onClick={handleUndo}
          className="ml-2 flex items-center justify-center p-1 rounded-full hover:bg-white/10 transition-colors group"
        >
          <span className="text-gray-400 group-hover:text-white text-[10px] sm:text-xs font-bold uppercase tracking-wide px-1">
            Undo
          </span>
        </button>
      </div>
    </div>
  );
}
