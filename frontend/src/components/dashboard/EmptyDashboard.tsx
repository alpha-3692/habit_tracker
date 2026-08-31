"use client";

import Link from "next/link";
import { Target, Plus } from "lucide-react";

interface EmptyDashboardProps {
  hasHabits: boolean;
}

export function EmptyDashboard({ hasHabits }: EmptyDashboardProps) {
  return (
    <div className="text-center py-16 bg-[#1a1a1a] border border-[#2e2e2e] rounded-2xl p-8 space-y-4 shadow-xl">
      <div className="w-14 h-14 rounded-2xl bg-indigo-600/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 mx-auto">
        <Target className="w-7 h-7" />
      </div>

      <div className="space-y-1 max-w-md mx-auto">
        <h3 className="text-lg font-bold text-white tracking-tight">
          {hasHabits ? "No habits scheduled for today" : "No active habits created yet"}
        </h3>
        <p className="text-xs text-neutral-400">
          {hasHabits
            ? "Enjoy your off-day! Or add a new habit to keep building your consistency."
            : "Create your first daily habit and start building sustainable streaks."}
        </p>
      </div>

      <div>
        <Link
          href="/habits"
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-xl shadow-lg shadow-indigo-600/20 transition"
        >
          <Plus className="w-4 h-4" />
          <span>{hasHabits ? "Manage Habits" : "Create First Habit"}</span>
        </Link>
      </div>
    </div>
  );
}
