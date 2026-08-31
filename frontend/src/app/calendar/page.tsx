"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/context/AuthContext";
import { analyticsApi } from "@/lib/api/analytics";
import { habitsApi } from "@/lib/api/habits";
import { CalendarDaySummary, Habit } from "@/types";
import { MonthlyCalendar } from "@/components/calendar/MonthlyCalendar";
import { ArrowLeft, Target, Sparkles, Filter, AlertCircle } from "lucide-react";

export default function CalendarPage() {
  const router = useRouter();
  const { user, accessToken, isLoading } = useAuth();

  const [currentDate, setCurrentDate] = useState(new Date());
  const [daysData, setDaysData] = useState<CalendarDaySummary[]>([]);
  const [habits, setHabits] = useState<Habit[]>([]);
  const [selectedHabitId, setSelectedHabitId] = useState<string>("");
  const [isFetching, setIsFetching] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchCalendar = async () => {
    if (!accessToken) return;
    try {
      setIsFetching(true);
      setError(null);

      const year = currentDate.getFullYear();
      const month = currentDate.getMonth();
      const startDateStr = `${year}-${String(month + 1).padStart(2, "0")}-01`;
      const lastDay = new Date(year, month + 1, 0).getDate();
      const endDateStr = `${year}-${String(month + 1).padStart(2, "0")}-${String(lastDay).padStart(2, "0")}`;

      const [calRes, habitsRes] = await Promise.all([
        analyticsApi.getCalendarSummary(
          accessToken,
          startDateStr,
          endDateStr,
          selectedHabitId || undefined
        ),
        habitsApi.getHabits(accessToken, { is_active: true }),
      ]);

      setDaysData(calRes.days);
      setHabits(habitsRes);
    } catch (err: any) {
      setError(err?.message || "Failed to load calendar data.");
    } finally {
      setIsFetching(false);
    }
  };

  useEffect(() => {
    if (!isLoading && !user) {
      router.push("/login");
      return;
    }
    if (accessToken) {
      fetchCalendar();
    }
  }, [isLoading, user, accessToken, currentDate, selectedHabitId]);

  const handlePrevMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1));
  };

  const handleNextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1));
  };

  const totalExpected = daysData.reduce((acc, d) => acc + d.expected, 0);
  const totalCompleted = daysData.reduce((acc, d) => acc + d.completed, 0);
  const monthRate = totalExpected > 0 ? Math.round((totalCompleted / totalExpected) * 100) : 0;

  return (
    <main className="min-h-screen bg-[#0f0f0f] text-white p-6 max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <header className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#2e2e2e] pb-6">
        <div className="space-y-1">
          <div className="flex items-center gap-3">
            <Link
              href="/dashboard"
              className="p-2 text-neutral-400 hover:text-white hover:bg-[#242424] rounded-xl border border-[#333] transition"
            >
              <ArrowLeft className="w-4 h-4" />
            </Link>
            <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight">
              Monthly Calendar
            </h1>
          </div>
          <p className="text-xs text-neutral-400 pl-11">
            Visual breakdown of your daily habit consistency across the month.
          </p>
        </div>

        {/* Habit Filter Dropdown */}
        <div className="flex items-center gap-2 self-start sm:self-auto">
          <Filter className="w-4 h-4 text-neutral-400" />
          <select
            value={selectedHabitId}
            onChange={(e) => setSelectedHabitId(e.target.value)}
            className="bg-[#1a1a1a] border border-[#333] focus:border-indigo-500 rounded-xl px-3 py-2 text-xs text-white outline-none transition"
          >
            <option value="">All Habits</option>
            {habits.map((h) => (
              <option key={h.id} value={h.id}>
                {h.title}
              </option>
            ))}
          </select>
        </div>
      </header>

      {/* Month Stats Card */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-[#1a1a1a] border border-[#2e2e2e] rounded-2xl p-5 space-y-1">
          <span className="text-xs font-semibold text-neutral-400 uppercase tracking-wider">
            Month Consistency
          </span>
          <p className="text-3xl font-extrabold text-emerald-400">{monthRate}%</p>
        </div>

        <div className="bg-[#1a1a1a] border border-[#2e2e2e] rounded-2xl p-5 space-y-1">
          <span className="text-xs font-semibold text-neutral-400 uppercase tracking-wider">
            Habits Completed
          </span>
          <p className="text-3xl font-extrabold text-white">{totalCompleted}</p>
        </div>

        <div className="bg-[#1a1a1a] border border-[#2e2e2e] rounded-2xl p-5 space-y-1">
          <span className="text-xs font-semibold text-neutral-400 uppercase tracking-wider">
            Total Expected
          </span>
          <p className="text-3xl font-extrabold text-white">{totalExpected}</p>
        </div>
      </div>

      {/* Calendar Grid */}
      <MonthlyCalendar
        currentDate={currentDate}
        daysData={daysData}
        onPrevMonth={handlePrevMonth}
        onNextMonth={handleNextMonth}
      />
    </main>
  );
}
