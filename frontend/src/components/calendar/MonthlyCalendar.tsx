"use client";

import { useState } from "react";
import { CalendarDaySummary } from "@/types";
import { ChevronLeft, ChevronRight, Check, AlertCircle, Minus, PieChart } from "lucide-react";

interface MonthlyCalendarProps {
  currentDate: Date;
  daysData: CalendarDaySummary[];
  onPrevMonth: () => void;
  onNextMonth: () => void;
  onSelectDate?: (dateStr: string) => void;
  selectedDate?: string | null;
}

const WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

export function MonthlyCalendar({
  currentDate,
  daysData,
  onPrevMonth,
  onNextMonth,
  onSelectDate,
  selectedDate,
}: MonthlyCalendarProps) {
  const [hoveredDay, setHoveredDay] = useState<CalendarDaySummary | null>(null);

  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();

  const monthName = currentDate.toLocaleString("default", { month: "long" });

  // Get total days in month
  const totalDays = new Date(year, month + 1, 0).getDate();

  // Get weekday of 1st day (0 = Sun in JS, convert to 0 = Mon)
  const firstDayWeekday = (new Date(year, month, 1).getDay() + 6) % 7;

  // Map daysData by date string (YYYY-MM-DD)
  const daysMap = new Map<string, CalendarDaySummary>();
  daysData.forEach((d) => daysMap.set(d.date, d));

  return (
    <div className="bg-[#1a1a1a] border border-[#2e2e2e] rounded-2xl p-6 shadow-xl space-y-6">
      {/* Month Navigation Header */}
      <div className="flex items-center justify-between">
        <div className="space-y-0.5">
          <h2 className="text-xl font-extrabold text-white tracking-tight">
            {monthName} {year}
          </h2>
          <p className="text-xs text-neutral-400">
            Daily consistency overview
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={onPrevMonth}
            className="p-2 text-neutral-400 hover:text-white hover:bg-[#242424] rounded-xl border border-[#333] transition"
            aria-label="Previous Month"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <button
            onClick={onNextMonth}
            className="p-2 text-neutral-400 hover:text-white hover:bg-[#242424] rounded-xl border border-[#333] transition"
            aria-label="Next Month"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Weekday Labels */}
      <div className="grid grid-cols-7 gap-2 text-center text-xs font-semibold text-neutral-400">
        {WEEKDAYS.map((wd) => (
          <div key={wd} className="py-1">
            {wd}
          </div>
        ))}
      </div>

      {/* Days Grid */}
      <div className="grid grid-cols-7 gap-2">
        {/* Leading empty days */}
        {Array.from({ length: firstDayWeekday }).map((_, i) => (
          <div key={`empty-${i}`} className="h-16 md:h-20 rounded-xl bg-transparent" />
        ))}

        {/* Month days */}
        {Array.from({ length: totalDays }).map((_, idx) => {
          const dayNum = idx + 1;
          const dateStr = `${year}-${String(month + 1).padStart(2, "0")}-${String(dayNum).padStart(2, "0")}`;
          const summary = daysMap.get(dateStr);
          const isSelected = selectedDate === dateStr;

          const hasExpected = summary && summary.expected > 0;
          const isFull = hasExpected && summary.percentage >= 100;
          const isPartial = hasExpected && summary.percentage > 0 && summary.percentage < 100;
          const isMissed = hasExpected && summary.percentage === 0;

          return (
            <button
              key={dateStr}
              onClick={() => onSelectDate?.(dateStr)}
              onMouseEnter={() => setHoveredDay(summary || null)}
              onMouseLeave={() => setHoveredDay(null)}
              className={`h-16 md:h-20 rounded-xl p-2 flex flex-col justify-between text-left border transition relative ${
                isSelected
                  ? "border-indigo-500 bg-indigo-950/20"
                  : "border-[#2e2e2e] hover:border-[#444] bg-[#222]"
              }`}
            >
              <div className="flex items-center justify-between w-full">
                <span
                  className={`text-xs font-semibold ${
                    hasExpected ? "text-white" : "text-neutral-500"
                  }`}
                >
                  {dayNum}
                </span>

                {/* Status Indicator Icon */}
                {isFull && (
                  <span className="w-5 h-5 rounded-md bg-emerald-500/20 text-emerald-400 flex items-center justify-center text-[10px] font-bold">
                    ✓
                  </span>
                )}
                {isPartial && (
                  <span className="w-5 h-5 rounded-md bg-indigo-500/20 text-indigo-400 flex items-center justify-center text-[10px] font-bold">
                    ◐
                  </span>
                )}
                {isMissed && (
                  <span className="w-5 h-5 rounded-md bg-rose-500/20 text-rose-400 flex items-center justify-center text-[10px] font-bold">
                    ✕
                  </span>
                )}
                {!hasExpected && (
                  <span className="w-5 h-5 text-neutral-600 flex items-center justify-center text-[10px]">
                    —
                  </span>
                )}
              </div>

              {/* Completion subtext */}
              {hasExpected && (
                <div className="space-y-1">
                  <div className="flex items-center justify-between text-[10px] text-neutral-400">
                    <span>
                      {summary.completed}/{summary.expected}
                    </span>
                    <span className="font-mono">{summary.percentage}%</span>
                  </div>
                  <div className="w-full bg-[#161616] h-1.5 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${
                        isFull
                          ? "bg-emerald-400"
                          : isPartial
                          ? "bg-indigo-400"
                          : "bg-rose-400"
                      }`}
                      style={{ width: `${summary.percentage}%` }}
                    />
                  </div>
                </div>
              )}
            </button>
          );
        })}
      </div>

      {/* Legend Footer */}
      <div className="flex items-center justify-between flex-wrap gap-4 pt-4 border-t border-[#2e2e2e] text-xs text-neutral-400">
        <div className="flex items-center gap-4 flex-wrap">
          <div className="flex items-center gap-1.5">
            <span className="w-4 h-4 rounded bg-emerald-500/20 text-emerald-400 flex items-center justify-center text-[10px] font-bold">
              ✓
            </span>
            <span>Completed (100%)</span>
          </div>

          <div className="flex items-center gap-1.5">
            <span className="w-4 h-4 rounded bg-indigo-500/20 text-indigo-400 flex items-center justify-center text-[10px] font-bold">
              ◐
            </span>
            <span>Partial (1–99%)</span>
          </div>

          <div className="flex items-center gap-1.5">
            <span className="w-4 h-4 rounded bg-rose-500/20 text-rose-400 flex items-center justify-center text-[10px] font-bold">
              ✕
            </span>
            <span>Missed</span>
          </div>

          <div className="flex items-center gap-1.5">
            <span className="w-4 h-4 rounded bg-transparent text-neutral-500 flex items-center justify-center text-[10px]">
              —
            </span>
            <span>No Habits Due</span>
          </div>
        </div>
      </div>
    </div>
  );
}
