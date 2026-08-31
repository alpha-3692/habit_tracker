"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/context/AuthContext";
import { analyticsApi } from "@/lib/api/analytics";
import { habitsApi } from "@/lib/api/habits";
import { CalendarDaySummary, Habit, AnalyticsTrendsResponse } from "@/types";
import { ConsistencyHeatmap } from "@/components/analytics/ConsistencyHeatmap";
import { MomentumScoreCard } from "@/components/analytics/MomentumScoreCard";
import { DayOfWeekAnalysis } from "@/components/analytics/DayOfWeekAnalysis";
import { CategoryBreakdown } from "@/components/analytics/CategoryBreakdown";
import { BehavioralInsightsList } from "@/components/analytics/BehavioralInsightsList";
import {
  ArrowLeft,
  Activity,
  Filter,
  Sparkles,
  Flame,
  Target,
  Calendar,
} from "lucide-react";

export default function AnalyticsPage() {
  const router = useRouter();
  const { user, accessToken, isLoading } = useAuth();

  const [daysData, setDaysData] = useState<CalendarDaySummary[]>([]);
  const [trendsData, setTrendsData] = useState<AnalyticsTrendsResponse | null>(null);
  const [habits, setHabits] = useState<Habit[]>([]);
  const [selectedHabitId, setSelectedHabitId] = useState<string>("");
  const [selectedDays, setSelectedDays] = useState<number>(30);
  const [isFetching, setIsFetching] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAnalyticsData = async () => {
    if (!accessToken) return;
    try {
      setIsFetching(true);
      setError(null);

      // Past 365 days range for Heatmap
      const today = new Date();
      const pastYear = new Date();
      pastYear.setDate(today.getDate() - 364);

      const startDateStr = pastYear.toISOString().split("T")[0];
      const endDateStr = today.toISOString().split("T")[0];

      const [calRes, trendsRes, habitsRes] = await Promise.all([
        analyticsApi.getCalendarSummary(
          accessToken,
          startDateStr,
          endDateStr,
          selectedHabitId || undefined
        ),
        analyticsApi.getAnalyticsTrends(accessToken, selectedDays),
        habitsApi.getHabits(accessToken, { is_active: true }),
      ]);

      setDaysData(calRes.days);
      setTrendsData(trendsRes);
      setHabits(habitsRes);
    } catch (err: any) {
      setError(err?.message || "Failed to load analytics data.");
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
      fetchAnalyticsData();
    }
  }, [isLoading, user, accessToken, selectedHabitId, selectedDays]);

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
              Consistency Analytics
            </h1>
          </div>
          <p className="text-xs text-neutral-400 pl-11">
            Understand your execution momentum, day-of-week rhythm, and category performance.
          </p>
        </div>

        {/* Controls */}
        <div className="flex items-center gap-2 self-start sm:self-auto flex-wrap">
          {/* Days Range Selector */}
          <select
            value={selectedDays}
            onChange={(e) => setSelectedDays(Number(e.target.value))}
            className="bg-[#1a1a1a] border border-[#333] focus:border-indigo-500 rounded-xl px-3 py-2 text-xs text-white outline-none transition"
          >
            <option value={14}>Last 14 Days</option>
            <option value={30}>Last 30 Days</option>
            <option value={90}>Last 90 Days</option>
          </select>

          {/* Habit Filter Dropdown */}
          <select
            value={selectedHabitId}
            onChange={(e) => setSelectedHabitId(e.target.value)}
            className="bg-[#1a1a1a] border border-[#333] focus:border-indigo-500 rounded-xl px-3 py-2 text-xs text-white outline-none transition"
          >
            <option value="">All Habits (Heatmap)</option>
            {habits.map((h) => (
              <option key={h.id} value={h.id}>
                {h.title}
              </option>
            ))}
          </select>
        </div>
      </header>

      {isFetching && !trendsData ? (
        <div className="py-24 text-center text-xs text-neutral-400 animate-pulse">
          Analyzing consistency patterns & momentum...
        </div>
      ) : (
        <>
          {/* 1. Momentum Score & Executive KPIs */}
          {trendsData && (
            <MomentumScoreCard
              score={trendsData.momentum_score}
              overallConsistency={trendsData.overall_consistency}
              totalHabits={trendsData.total_habits_tracked}
              totalCompletions={trendsData.total_completions}
            />
          )}

          {/* 2. Automated Behavioral Insights */}
          {trendsData && trendsData.insights.length > 0 && (
            <BehavioralInsightsList insights={trendsData.insights} />
          )}

          {/* 3. Day of Week Analysis */}
          {trendsData && (
            <DayOfWeekAnalysis dayOfWeekData={trendsData.day_of_week} />
          )}

          {/* 4. Category Breakdown */}
          {trendsData && (
            <CategoryBreakdown categoryData={trendsData.category_breakdown} />
          )}

          {/* 5. 365-Day Consistency Heatmap */}
          <ConsistencyHeatmap days={daysData} />
        </>
      )}
    </main>
  );
}
