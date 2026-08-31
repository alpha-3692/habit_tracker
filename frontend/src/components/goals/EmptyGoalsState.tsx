"use client";

import { Target, Plus } from "lucide-react";

interface EmptyGoalsStateProps {
  onCreate: () => void;
}

export function EmptyGoalsState({ onCreate }: EmptyGoalsStateProps) {
  return (
    <div className="text-center py-16 bg-[#1a1a1a] border border-[#2e2e2e] rounded-2xl p-8 space-y-4 shadow-xl">
      <div className="w-14 h-14 rounded-2xl bg-indigo-600/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 mx-auto">
        <Target className="w-7 h-7" />
      </div>

      <div className="space-y-1 max-w-md mx-auto">
        <h3 className="text-lg font-bold text-white tracking-tight">
          No goals defined yet
        </h3>
        <p className="text-xs text-neutral-400">
          Goals give direction to your daily habits. Create your first goal and link habits to measure real progress.
        </p>
      </div>

      <div>
        <button
          onClick={onCreate}
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-xl shadow-lg shadow-indigo-600/20 transition"
        >
          <Plus className="w-4 h-4" />
          <span>Create First Goal</span>
        </button>
      </div>
    </div>
  );
}
