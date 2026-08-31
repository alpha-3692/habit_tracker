"use client";

import { CategoryPerformanceItem } from "@/types";
import { Layers, Target } from "lucide-react";

interface CategoryBreakdownProps {
  categoryData: CategoryPerformanceItem[];
}

export function CategoryBreakdown({ categoryData }: CategoryBreakdownProps) {
  if (!categoryData || categoryData.length === 0) {
    return (
      <div className="bg-[#1a1a1a] border border-[#2e2e2e] rounded-2xl p-6 shadow-xl space-y-4">
        <h2 className="text-xl font-extrabold text-white tracking-tight">Category Breakdown</h2>
        <p className="text-xs text-neutral-400">No category habits tracked in this period.</p>
      </div>
    );
  }

  return (
    <div className="bg-[#1a1a1a] border border-[#2e2e2e] rounded-2xl p-6 shadow-xl space-y-6">
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Layers className="w-5 h-5 text-indigo-400" />
            <h2 className="text-xl font-extrabold text-white tracking-tight">
              Category Breakdown
            </h2>
          </div>
          <p className="text-xs text-neutral-400">
            Compare consistency performance across different areas of your life.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {categoryData.map((cat) => (
          <div
            key={cat.category}
            className="bg-[#242424] border border-[#333] hover:border-[#444] rounded-xl p-4 space-y-3 transition"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="px-2 py-0.5 rounded-md bg-[#161616] text-neutral-300 text-xs font-semibold capitalize">
                  {cat.category.replace("_", " ")}
                </span>
                <span className="text-[11px] text-neutral-500">
                  ({cat.habit_count} {cat.habit_count === 1 ? "habit" : "habits"})
                </span>
              </div>
              <span className="text-sm font-mono font-bold text-white">
                {cat.percentage}%
              </span>
            </div>

            <div className="w-full bg-[#161616] h-2 rounded-full overflow-hidden p-0.5">
              <div
                className="bg-gradient-to-r from-indigo-500 to-emerald-400 h-full rounded-full transition-all duration-500"
                style={{ width: `${cat.percentage}%` }}
              />
            </div>

            <div className="flex items-center justify-between text-[11px] text-neutral-400">
              <span>{cat.completed} completed</span>
              <span>{cat.expected} scheduled</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
