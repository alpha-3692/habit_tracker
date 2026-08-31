"use client";

import { useState } from "react";
import { CalendarDaySummary } from "@/types";

interface ConsistencyHeatmapProps {
  days: CalendarDaySummary[];
}

export function ConsistencyHeatmap({ days }: ConsistencyHeatmapProps) {
  const [hovered, setHovered] = useState<CalendarDaySummary | null>(null);
  const [tooltipPos, setTooltipPos] = useState<{ x: number; y: number } | null>(null);

  const daysMap = new Map<string, CalendarDaySummary>();
  days.forEach((d) => daysMap.set(d.date, d));

  // Determine cell color based on normalized completion percentage
  const getCellColor = (summary?: CalendarDaySummary) => {
    if (!summary || summary.expected === 0) return "bg-[#222] border-[#2e2e2e]";
    const pct = summary.percentage;
    if (pct === 0) return "bg-rose-950/40 border-rose-900/40";
    if (pct <= 25) return "bg-indigo-950 border-indigo-900";
    if (pct <= 50) return "bg-indigo-800 border-indigo-700";
    if (pct <= 75) return "bg-indigo-600 border-indigo-500";
    return "bg-emerald-500 border-emerald-400";
  };

  // Group days into columns of weeks (7 days each)
  const weeks: CalendarDaySummary[][] = [];
  let currentWeek: CalendarDaySummary[] = [];

  days.forEach((day, index) => {
    currentWeek.push(day);
    if (currentWeek.length === 7 || index === days.length - 1) {
      weeks.push(currentWeek);
      currentWeek = [];
    }
  });

  return (
    <div className="bg-[#1a1a1a] border border-[#2e2e2e] rounded-2xl p-6 shadow-xl space-y-6 relative">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-extrabold text-white tracking-tight">
            Consistency Heatmap
          </h2>
          <p className="text-xs text-neutral-400">
            Last 12 months completion intensity
          </p>
        </div>
      </div>

      {/* Heatmap Grid Container with horizontal scroll */}
      <div className="overflow-x-auto pb-2">
        <div className="inline-flex gap-1 min-w-[700px]">
          {weeks.map((week, wIndex) => (
            <div key={`week-${wIndex}`} className="flex flex-col gap-1">
              {week.map((day) => {
                const isSelected = hovered?.date === day.date;
                return (
                  <div
                    key={day.date}
                    onMouseEnter={(e) => {
                      setHovered(day);
                      const rect = e.currentTarget.getBoundingClientRect();
                      setTooltipPos({ x: rect.left, y: rect.top });
                    }}
                    onMouseLeave={() => {
                      setHovered(null);
                      setTooltipPos(null);
                    }}
                    className={`w-3.5 h-3.5 rounded-sm border cursor-pointer transition-all ${getCellColor(
                      day
                    )} ${isSelected ? "ring-2 ring-white scale-125 z-10" : ""}`}
                  />
                );
              })}
            </div>
          ))}
        </div>
      </div>

      {/* Hover Tooltip Overlay */}
      {hovered && (
        <div className="p-3 bg-[#242424] border border-[#3e3e3e] rounded-xl text-xs space-y-1 shadow-2xl max-w-xs">
          <p className="font-bold text-white">
            {new Date(hovered.date).toLocaleDateString("en-US", {
              weekday: "short",
              month: "short",
              day: "numeric",
              year: "numeric",
            })}
          </p>
          <p className="text-neutral-300">
            {hovered.expected > 0
              ? `${hovered.completed} of ${hovered.expected} habits completed (${hovered.percentage}%)`
              : "No habits scheduled"}
          </p>
        </div>
      )}

      {/* Legend */}
      <div className="flex items-center justify-between pt-4 border-t border-[#2e2e2e] text-xs text-neutral-400">
        <span>365 Days Consistency</span>

        <div className="flex items-center gap-2">
          <span>Less</span>
          <div className="w-3 h-3 rounded-sm bg-[#222] border border-[#2e2e2e]" title="0%" />
          <div className="w-3 h-3 rounded-sm bg-indigo-950 border border-indigo-900" title="1-25%" />
          <div className="w-3 h-3 rounded-sm bg-indigo-800 border border-indigo-700" title="26-50%" />
          <div className="w-3 h-3 rounded-sm bg-indigo-600 border border-indigo-500" title="51-75%" />
          <div className="w-3 h-3 rounded-sm bg-emerald-500 border border-emerald-400" title="76-100%" />
          <span>More</span>
        </div>
      </div>
    </div>
  );
}
