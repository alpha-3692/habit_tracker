"use client";

import { CheckCircle2, Target } from "lucide-react";

interface TodayProgressProps {
  completedCount: number;
  totalExpected: number;
  percentage: number;
}

export function TodayProgress({
  completedCount,
  totalExpected,
  percentage,
}: TodayProgressProps) {
  return (
    <div className="bg-[#1a1a1a] border border-[#2e2e2e] rounded-2xl p-6 shadow-xl relative overflow-hidden space-y-4">
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <span className="text-xs font-semibold text-neutral-400 uppercase tracking-wider">
            Today's Progress
          </span>
          <div className="flex items-baseline gap-3">
            <span className="text-4xl font-extrabold text-white tracking-tight">
              {percentage}%
            </span>
            <span className="text-sm text-neutral-400 font-medium">
              {completedCount} of {totalExpected} completed
            </span>
          </div>
        </div>

        <div className="w-12 h-12 rounded-2xl bg-indigo-600/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
          <CheckCircle2 className="w-6 h-6" />
        </div>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-[#242424] h-3 rounded-full overflow-hidden p-0.5 border border-[#333]">
        <div
          className="bg-gradient-to-r from-indigo-500 to-emerald-400 h-full rounded-full transition-all duration-500 ease-out"
          style={{ width: `${Math.min(100, Math.max(0, percentage))}%` }}
        />
      </div>
    </div>
  );
}
