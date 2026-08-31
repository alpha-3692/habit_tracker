"use client";

import { DayOfWeekItem } from "@/types";
import { Calendar, TrendingUp } from "lucide-react";

interface DayOfWeekAnalysisProps {
  dayOfWeekData: DayOfWeekItem[];
}

export function DayOfWeekAnalysis({ dayOfWeekData }: DayOfWeekAnalysisProps) {
  const maxPct = Math.max(...dayOfWeekData.map((d) => d.percentage), 1);
  const bestDay = dayOfWeekData.filter((d) => d.expected > 0).sort((a, b) => b.percentage - a.percentage)[0];

  return (
    <div className="bg-[#1a1a1a] border border-[#2e2e2e] rounded-2xl p-6 shadow-xl space-y-6">
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Calendar className="w-5 h-5 text-indigo-400" />
            <h2 className="text-xl font-extrabold text-white tracking-tight">
              Day-of-Week Consistency
            </h2>
          </div>
          <p className="text-xs text-neutral-400">
            Identify which days of the week have your strongest and weakest follow-through.
          </p>
        </div>

        {bestDay && bestDay.percentage > 0 && (
          <div className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-emerald-400 text-xs font-bold">
            <TrendingUp className="w-3.5 h-3.5" />
            <span>Peak: {bestDay.day_name} ({bestDay.percentage}%)</span>
          </div>
        )}
      </div>

      <div className="space-y-3">
        {dayOfWeekData.map((item) => {
          const isBest = bestDay && bestDay.day_index === item.day_index && item.percentage > 0;
          return (
            <div key={item.day_name} className="space-y-1.5">
              <div className="flex items-center justify-between text-xs">
                <span className={`font-semibold ${isBest ? "text-emerald-400 font-bold" : "text-neutral-300"}`}>
                  {item.day_name}
                  {isBest && " ★"}
                </span>
                <div className="flex items-center gap-3 text-neutral-400">
                  <span>
                    {item.completed} / {item.expected} completed
                  </span>
                  <span className="font-mono font-bold text-white w-12 text-right">
                    {item.percentage}%
                  </span>
                </div>
              </div>

              <div className="w-full bg-[#242424] h-2.5 rounded-full overflow-hidden p-0.5 border border-[#333]">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    item.percentage >= 80
                      ? "bg-emerald-400"
                      : item.percentage >= 50
                      ? "bg-indigo-500"
                      : item.percentage > 0
                      ? "bg-amber-400"
                      : "bg-neutral-700"
                  }`}
                  style={{ width: `${item.percentage}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
