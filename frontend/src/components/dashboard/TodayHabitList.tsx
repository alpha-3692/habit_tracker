"use client";

import { Habit } from "@/types";
import { CheckCircle2, Flame } from "lucide-react";

interface TodayHabitListProps {
  habits: Habit[];
  onComplete: (habitId: string) => Promise<void>;
  loadingId: string | null;
}

export function TodayHabitList({
  habits,
  onComplete,
  loadingId,
}: TodayHabitListProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold text-white tracking-tight">Today's Habits</h2>
        <span className="text-xs text-neutral-400 font-medium">
          {habits.length} habits scheduled
        </span>
      </div>

      <div className="space-y-3">
        {habits.map((habit) => {
          const isCompleted = habit.completed_today;
          const isLoadingThis = loadingId === habit.id;

          return (
            <div
              key={habit.id}
              className={`bg-[#1a1a1a] border rounded-2xl p-4 flex items-center justify-between gap-4 transition shadow-md ${
                isCompleted
                  ? "border-emerald-500/20 bg-emerald-950/10"
                  : "border-[#2e2e2e] hover:border-[#3e3e3e]"
              }`}
            >
              <div className="space-y-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="px-2 py-0.5 rounded-md bg-[#242424] text-neutral-400 text-[10px] font-semibold uppercase tracking-wider">
                    {habit.category}
                  </span>

                  {/* Streak badge */}
                  <div className="flex items-center gap-1 text-xs font-bold text-amber-400">
                    <Flame className="w-3.5 h-3.5 text-amber-500 fill-amber-500" />
                    <span>{habit.current_streak}d</span>
                  </div>
                </div>

                <h3
                  className={`text-sm font-bold truncate ${
                    isCompleted ? "line-through text-neutral-400" : "text-white"
                  }`}
                >
                  {habit.title}
                </h3>

                {habit.target_value && (
                  <p className="text-xs text-neutral-400 font-medium">
                    Target: {habit.target_value} {habit.target_unit || ""}
                  </p>
                )}
              </div>

              {/* Complete Toggle Button */}
              <button
                onClick={() => onComplete(habit.id)}
                disabled={isCompleted || isLoadingThis}
                className={`flex-shrink-0 flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition ${
                  isCompleted
                    ? "bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 cursor-default"
                    : "bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-600/20 disabled:opacity-50"
                }`}
              >
                <CheckCircle2 className="w-4 h-4" />
                <span>
                  {isLoadingThis
                    ? "Saving..."
                    : isCompleted
                    ? "Completed"
                    : "Complete"}
                </span>
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}
