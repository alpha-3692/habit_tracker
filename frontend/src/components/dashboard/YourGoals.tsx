"use client";

import Link from "next/link";
import { Goal } from "@/types";
import { Target, ArrowRight, Plus } from "lucide-react";

interface YourGoalsProps {
  goals: Goal[];
}

export function YourGoals({ goals }: YourGoalsProps) {
  if (!goals || goals.length === 0) {
    return (
      <div className="bg-[#1a1a1a] border border-[#2e2e2e] rounded-2xl p-5 flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-indigo-600/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
            <Target className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white">No active goals yet</h3>
            <p className="text-xs text-neutral-400">
              Connect your daily habits to meaningful long-term outcomes.
            </p>
          </div>
        </div>

        <Link
          href="/goals"
          className="flex items-center gap-1.5 px-3 py-1.5 bg-[#242424] hover:bg-[#2e2e2e] border border-[#333] text-white text-xs font-semibold rounded-xl transition flex-shrink-0"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>Add Goal</span>
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold text-white tracking-tight">Your Goals</h2>
        <Link
          href="/goals"
          className="flex items-center gap-1 text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition"
        >
          <span>View All</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </Link>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {goals.slice(0, 4).map((goal) => (
          <div
            key={goal.id}
            className="bg-[#1a1a1a] border border-[#2e2e2e] hover:border-[#3e3e3e] rounded-2xl p-4 space-y-3 transition"
          >
            <div className="flex items-center justify-between gap-2">
              <span className="px-2 py-0.5 rounded-md bg-[#242424] text-neutral-400 text-[10px] font-semibold uppercase tracking-wider">
                {goal.category}
              </span>
              <span className="text-xs font-mono font-bold text-white">
                {goal.progress_percentage}%
              </span>
            </div>

            <div>
              <h3 className="text-sm font-bold text-white truncate">{goal.title}</h3>
              <p className="text-xs text-neutral-400">
                {goal.habit_count} {goal.habit_count === 1 ? "habit" : "habits"} linked
              </p>
            </div>

            <div className="w-full bg-[#242424] h-2 rounded-full overflow-hidden p-0.5 border border-[#333]">
              <div
                className="bg-gradient-to-r from-indigo-500 to-emerald-400 h-full rounded-full transition-all duration-500"
                style={{ width: `${Math.min(100, Math.max(0, goal.progress_percentage))}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
