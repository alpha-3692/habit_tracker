"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/context/AuthContext";
import { historyApi } from "@/lib/api/history";
import { HabitHistoryResponse, DayHistory } from "@/types";
import {
  ArrowLeft,
  Flame,
  CheckCircle2,
  Calendar as CalendarIcon,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  AlertCircle,
  Activity,
} from "lucide-react";

export default function HabitDetailPage() {
  const params = useParams();
  const router = useRouter();
  const habitId = params.id as string;
  const { user, accessToken, isLoading } = useAuth();

  const [historyData, setHistoryData] = useState<HabitHistoryResponse | null>(null);
  const [isFetching, setIsFetching] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentDate, setCurrentDate] = useState(new Date());

  const fetchHistory = async () => {
    if (!accessToken || !habitId) return;
    try {
      setIsFetching(true);
      setError(null);

      // Fetch for current month view
      const year = currentDate.getFullYear();
      const month = currentDate.getMonth();
      const startDateStr = `${year}-${String(month + 1).padStart(2, "0")}-01`;
      const lastDay = new Date(year, month + 1, 0).getDate();
      const endDateStr = `${year}-${String(month + 1).padStart(2, "0")}-${String(lastDay).padStart(2, "0")}`;

      const res = await historyApi.getHabitHistory(
        accessToken,
        habitId,
        startDateStr,
        endDateStr
      );
      setHistoryData(res);
    } catch (err: any) {
      setError(err?.message || "Failed to load habit history.");
    } finally {
      setIsFetching(false);
    }
  };

  useEffect(() => {
    if (!isLoading && !user) {
      router.push("/login");
      return;
    }
    if (accessToken && habitId) {
      fetchHistory();
    }
  }, [isLoading, user, accessToken, habitId, currentDate]);

  const handlePrevMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1));
  };

  const handleNextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1));
  };

  if (isLoading || isFetching) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#0f0f0f] text-neutral-400">
        <p className="animate-pulse text-xs font-medium">Loading habit history...</p>
      </div>
    );
  }

  if (error || !historyData) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-[#0f0f0f] text-white p-6 space-y-4">
        <AlertCircle className="w-8 h-8 text-red-400" />
        <p className="text-sm text-neutral-300">{error || "Habit not found."}</p>
        <Link
          href="/habits"
          className="px-4 py-2 bg-[#242424] hover:bg-[#2e2e2e] text-xs font-semibold rounded-xl border border-[#333]"
        >
          Back to Habits
        </Link>
      </div>
    );
  }

  const { habit, days } = historyData;
  const monthName = currentDate.toLocaleString("default", { month: "long" });
  const year = currentDate.getFullYear();
  const completedInMonth = days.filter((d) => d.is_completed).length;
  const dueInMonth = days.filter((d) => d.is_due).length;
  const monthPct = dueInMonth > 0 ? Math.round((completedInMonth / dueInMonth) * 100) : 0;

  return (
    <main className="min-h-screen bg-[#0f0f0f] text-white p-6 max-w-4xl mx-auto space-y-8">
      {/* Header Navigation */}
      <div className="flex items-center justify-between border-b border-[#2e2e2e] pb-6">
        <div className="flex items-center gap-3">
          <Link
            href="/habits"
            className="p-2 text-neutral-400 hover:text-white hover:bg-[#242424] rounded-xl border border-[#333] transition"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <div className="flex items-center gap-2">
              <span className="px-2 py-0.5 rounded-md bg-[#242424] text-neutral-400 text-[10px] font-semibold uppercase tracking-wider">
                {habit.category}
              </span>
              <span className="px-2 py-0.5 rounded-md bg-[#242424] text-neutral-400 text-[10px] font-semibold uppercase tracking-wider">
                {habit.frequency_type.replace("_", " ")}
              </span>
            </div>
            <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight mt-1">
              {habit.title}
            </h1>
          </div>
        </div>
      </div>

      {/* Streak Stats Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-[#1a1a1a] border border-[#2e2e2e] rounded-2xl p-4 space-y-1">
          <span className="text-[11px] font-semibold text-neutral-400 uppercase tracking-wider">
            Current Streak
          </span>
          <div className="flex items-center gap-1.5 text-xl font-extrabold text-amber-400">
            <Flame className="w-5 h-5 text-amber-500 fill-amber-500" />
            <span>{habit.current_streak} days</span>
          </div>
        </div>

        <div className="bg-[#1a1a1a] border border-[#2e2e2e] rounded-2xl p-4 space-y-1">
          <span className="text-[11px] font-semibold text-neutral-400 uppercase tracking-wider">
            Best Streak
          </span>
          <p className="text-xl font-extrabold text-white">{habit.best_streak} days</p>
        </div>

        <div className="bg-[#1a1a1a] border border-[#2e2e2e] rounded-2xl p-4 space-y-1">
          <span className="text-[11px] font-semibold text-neutral-400 uppercase tracking-wider">
            Total Completions
          </span>
          <p className="text-xl font-extrabold text-white">{habit.total_completions}</p>
        </div>

        <div className="bg-[#1a1a1a] border border-[#2e2e2e] rounded-2xl p-4 space-y-1">
          <span className="text-[11px] font-semibold text-neutral-400 uppercase tracking-wider">
            Month Rate
          </span>
          <p className="text-xl font-extrabold text-emerald-400">{monthPct}%</p>
        </div>
      </div>

      {/* Monthly History View */}
      <div className="bg-[#1a1a1a] border border-[#2e2e2e] rounded-2xl p-6 space-y-6 shadow-xl">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-white tracking-tight">
            {monthName} {year} History
          </h2>
          <div className="flex items-center gap-2">
            <button
              onClick={handlePrevMonth}
              className="p-2 text-neutral-400 hover:text-white hover:bg-[#242424] rounded-xl border border-[#333] transition"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              onClick={handleNextMonth}
              className="p-2 text-neutral-400 hover:text-white hover:bg-[#242424] rounded-xl border border-[#333] transition"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Days Grid */}
        <div className="grid grid-cols-7 gap-2">
          {days.map((d) => {
            const dayNum = new Date(d.date).getDate();
            return (
              <div
                key={d.date}
                className={`p-3 rounded-xl border flex flex-col justify-between h-16 ${
                  d.is_completed
                    ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-400"
                    : d.is_due
                    ? "bg-rose-500/10 border-rose-500/20 text-rose-400"
                    : "bg-[#242424] border-[#333] text-neutral-500"
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold">{dayNum}</span>
                  <span className="text-[11px] font-bold">
                    {d.is_completed ? "✓" : d.is_due ? "✕" : "—"}
                  </span>
                </div>
                <span className="text-[10px] truncate">
                  {d.is_completed ? "Completed" : d.is_due ? "Missed" : "Off day"}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </main>
  );
}
