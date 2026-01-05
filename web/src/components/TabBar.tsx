/**
 * TabBar component for filtering library books by status
 */

import type { ReadingStatus } from '../types/book';

export interface StatusCounts {
  to_read: number;
  did_not_finish: number;
  completed: number;
}

interface TabBarProps {
  activeTab: ReadingStatus;
  counts: StatusCounts;
  onTabChange: (tab: ReadingStatus) => void;
}

const TAB_CONFIG: { status: ReadingStatus; label: string }[] = [
  { status: 'to_read', label: 'To Read' },
  { status: 'did_not_finish', label: "Didn't Finish" },
  { status: 'completed', label: 'Completed' },
];

export function TabBar({ activeTab, counts, onTabChange }: TabBarProps) {
  return (
    <div className="flex items-center space-x-3 mb-8 overflow-x-auto no-scrollbar pb-1">
      {TAB_CONFIG.map(({ status, label }) => {
        const isActive = activeTab === status;
        const count = counts[status];

        return (
          <button
            key={status}
            onClick={() => onTabChange(status)}
            className={`relative px-6 py-2.5 rounded-full font-medium transition-all flex items-center gap-2 whitespace-nowrap ${
              isActive
                ? 'bg-primary text-white font-semibold shadow-md shadow-blue-500/20'
                : 'bg-white text-text-sub-light hover:text-text-main-light hover:bg-gray-50 shadow-sm'
            }`}
          >
            {label}
            <span
              className={`flex items-center justify-center min-w-[20px] h-5 px-1.5 rounded-full text-xs font-bold ${
                isActive ? 'bg-white/20' : 'bg-gray-100'
              }`}
            >
              {count}
            </span>
          </button>
        );
      })}
    </div>
  );
}
