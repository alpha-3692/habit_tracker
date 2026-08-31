"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/context/AuthContext";
import { achievementsApi } from "@/lib/api/achievements";
import { AchievementWithProgress } from "@/types";
import { AchievementProgress } from "@/components/achievements/AchievementProgress";
import { AchievementGrid } from "@/components/achievements/AchievementGrid";
import { ArrowLeft, Trophy, Sparkles } from "lucide-react";

export default function AchievementsPage() {
  const router = useRouter();
  const { user, accessToken, isLoading } = useAuth();

  const [achievements, setAchievements] = useState<AchievementWithProgress[]>([]);
  const [isFetching, setIsFetching] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAchievements = async () => {
    if (!accessToken) return;
    try {
      setIsFetching(true);
      setError(null);
      const data = await achievementsApi.getMyAchievements(accessToken);
      setAchievements(data);
    } catch (err: any) {
      setError(err?.message || "Failed to load achievements.");
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
      fetchAchievements();
    }
  }, [isLoading, user, accessToken]);

  return (
    <main className="min-h-screen bg-[#0f0f0f] text-white p-6 max-w-5xl mx-auto space-y-8">
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
              Badges & Milestones
            </h1>
          </div>
          <p className="text-xs text-neutral-400 pl-11">
            Track your milestones, streaks, completions, and progress towards unlocked honors.
          </p>
        </div>
      </header>

      {isFetching ? (
        <div className="py-24 text-center text-xs text-neutral-400 animate-pulse">
          Loading achievement milestones...
        </div>
      ) : error ? (
        <div className="p-6 bg-rose-950/20 border border-rose-900/40 rounded-2xl text-xs text-rose-300 text-center">
          {error}
        </div>
      ) : (
        <>
          {/* Progress Overview */}
          <AchievementProgress achievements={achievements} />

          {/* Achievement Grid with Filters */}
          <AchievementGrid achievements={achievements} />
        </>
      )}
    </main>
  );
}
