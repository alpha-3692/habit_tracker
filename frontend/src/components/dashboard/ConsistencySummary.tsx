"use client";

import { Activity, Flame, Target } from "lucide-react";

interface ConsistencySummaryProps {
  totalActiveHabits: number;
  totalCompletionsAllTime: number;
  bestStreakOverall: number;
}

export function ConsistencySummary({
  totalActiveHabits,
  totalCompletionsAllTime,
  bestStreakOverall,
}: ConsistencySummaryProps) {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold text-white tracking-tight">Consistency Summary</h2>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-[#1a1a1a] border border-[#2e2e2e] rounded-2xl p-5 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-neutral-400 uppercase tracking-wider">
              Active Habits
            </span>
            <Target className="w-4 h-4 text-indigo-400" />
          </div>
          <p className="text-2xl font-extrabold text-white">{totalActiveHabits}</p>
        </div>

        <div className="bg-[#1a1a1a] border border-[#2e2e2e] rounded-2xl p-5 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-neutral-400 uppercase tracking-wider">
              Total Completions
            </span>
            <Activity className="w-4 h-4 text-emerald-400" />
          </div>
          <p className="text-2xl font-extrabold text-white">{totalCompletionsAllTime}</p>
        </div>

        <div className="bg-[#1a1a1a] border border-[#2e2e2e] rounded-2xl p-5 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-neutral-400 uppercase tracking-wider">
              Best Streak
            </span>
            <Flame className="w-4 h-4 text-amber-500 fill-amber-500" />
          </div>
          <p className="text-2xl font-extrabold text-white">{bestStreakOverall} days</p>
        </div>
      </div>
    </div>
  );
}
