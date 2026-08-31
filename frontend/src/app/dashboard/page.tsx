"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import { dashboardApi, DashboardResponseData } from "@/lib/api/dashboard";
import { habitsApi } from "@/lib/api/habits";
import { DashboardHeader } from "@/components/dashboard/DashboardHeader";
import { TodayProgress } from "@/components/dashboard/TodayProgress";
import { TodayHabitList } from "@/components/dashboard/TodayHabitList";
import { ConsistencySummary } from "@/components/dashboard/ConsistencySummary";
import { YourGoals } from "@/components/dashboard/YourGoals";
import { EmptyDashboard } from "@/components/dashboard/EmptyDashboard";
import { NextReminderWidget } from "@/components/dashboard/NextReminderWidget";
import { AchievementUnlockedToast } from "@/components/achievements/AchievementUnlockedToast";
import { AlertCircle, RefreshCw, X } from "lucide-react";

export default function DashboardPage() {
  const router = useRouter();
  const { user, accessToken, isLoading, logout } = useAuth();

  const [data, setData] = useState<DashboardResponseData | null>(null);
  const [isFetching, setIsFetching] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [loadingId, setLoadingId] = useState<string | null>(null);
  const [unlockedAchievementCode, setUnlockedAchievementCode] = useState<string | null>(null);

  const fetchDashboardData = async () => {
    if (!accessToken) return;
    try {
      setIsFetching(true);
      setError(null);
      const res = await dashboardApi.getDashboard(accessToken);
      setData(res);
    } catch (err: any) {
      setError(err?.message || "Failed to load dashboard data.");
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
      fetchDashboardData();
    }
  }, [isLoading, user, accessToken]);

  const handleCompleteHabit = async (habitId: string) => {
    if (!accessToken || !data) return;
    try {
      setLoadingId(habitId);
      const res = await habitsApi.completeHabit(accessToken, habitId);
      
      // Check if newly unlocked achievements
      if (res && res.achievements_unlocked && res.achievements_unlocked.length > 0) {
        setUnlockedAchievementCode(res.achievements_unlocked[0]);
      }

      // Re-fetch dashboard to update progress percentage and streaks authoritatively
      const updatedData = await dashboardApi.getDashboard(accessToken);
      setData(updatedData);
    } catch (err: any) {
      setError(err?.message || "Failed to mark habit as completed.");
    } finally {
      setLoadingId(null);
    }
  };

  if (isLoading || isFetching) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#0f0f0f] text-neutral-400">
        <p className="animate-pulse text-sm font-medium">Loading Dashboard...</p>
      </div>
    );
  }

  if (!user || !data) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-[#0f0f0f] text-white p-6 space-y-4">
        <AlertCircle className="w-8 h-8 text-red-400" />
        <p className="text-sm text-neutral-300">
          {error || "Unable to load dashboard data."}
        </p>
        <button
          onClick={fetchDashboardData}
          className="flex items-center gap-2 px-4 py-2 bg-[#242424] hover:bg-[#2e2e2e] text-xs font-semibold rounded-xl border border-[#333]"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Retry</span>
        </button>
      </div>
    );
  }

  const { today, consistency_summary, goals } = data;
  const hasDueHabits = today.habits.length > 0;

  return (
    <main className="min-h-screen bg-[#0f0f0f] text-white p-6 max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <DashboardHeader
        fullName={data.user.full_name}
        currentDateStr={data.user.current_date}
        timezone={data.user.timezone}
        onLogout={() => {
          logout();
          router.push("/login");
        }}
      />

      {/* Next Upcoming Reminder Indicator */}
      {accessToken && <NextReminderWidget accessToken={accessToken} />}

      {/* Error Callout */}
      {error && (
        <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-xs flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
          <button onClick={() => setError(null)} className="text-red-400 hover:text-white">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Today's Progress Bar */}
      {hasDueHabits && (
        <TodayProgress
          completedCount={today.completed_habits}
          totalExpected={today.total_expected_habits}
          percentage={today.completion_percentage}
        />
      )}

      {/* Today's Habits Checklist OR Empty State */}
      {hasDueHabits ? (
        <TodayHabitList
          habits={today.habits}
          onComplete={handleCompleteHabit}
          loadingId={loadingId}
        />
      ) : (
        <EmptyDashboard hasHabits={consistency_summary.total_active_habits > 0} />
      )}

      {/* Your Goals Section */}
      <YourGoals goals={goals || []} />

      {/* Consistency Summary Metrics */}
      <ConsistencySummary
        totalActiveHabits={consistency_summary.total_active_habits}
        totalCompletionsAllTime={consistency_summary.total_completions_all_time}
        bestStreakOverall={consistency_summary.best_streak_overall}
      />

      {/* Achievement Unlocked Toast Notification */}
      {unlockedAchievementCode && (
        <AchievementUnlockedToast
          achievementCode={unlockedAchievementCode}
          onClose={() => setUnlockedAchievementCode(null)}
        />
      )}
    </main>
  );
}
