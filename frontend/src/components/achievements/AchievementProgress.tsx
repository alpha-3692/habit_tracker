"use client";

import { Trophy, Award, Zap, Flame } from "lucide-react";
import { AchievementWithProgress } from "@/types";

interface AchievementProgressProps {
  achievements: AchievementWithProgress[];
}

export function AchievementProgress({ achievements }: AchievementProgressProps) {
  const totalCount = achievements.length;
  const unlockedCount = achievements.filter((a) => a.is_unlocked).length;
  const percentage = totalCount > 0 ? Math.round((unlockedCount / totalCount) * 100) : 0;

  const streakCount = achievements.filter((a) => a.category === "streak" && a.is_unlocked).length;
  const completionCount = achievements.filter((a) => a.category === "completion" && a.is_unlocked).length;
  const habitCount = achievements.filter((a) => a.category === "habit" && a.is_unlocked).length;
  const goalCount = achievements.filter((a) => a.category === "goal" && a.is_unlocked).length;

  return (
    <div className="bg-[#1a1a1a] border border-[#2e2e2e] rounded-2xl p-6 shadow-xl space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Trophy className="w-5 h-5 text-amber-400" />
            <h2 className="text-xl font-extrabold text-white tracking-tight">
              Milestone Progress
            </h2>
          </div>
          <p className="text-xs text-neutral-400">
            Earn badges and celebrate consistency breakthroughs as you build lasting daily habits.
          </p>
        </div>

        <div className="flex items-baseline gap-2 self-start sm:self-auto">
          <span className="text-3xl font-extrabold text-amber-400">
            {unlockedCount}
          </span>
          <span className="text-xs text-neutral-500 font-mono">/ {totalCount} Unlocked</span>
        </div>
      </div>

      {/* Main Overall Progress Bar */}
      <div className="space-y-2">
        <div className="flex items-center justify-between text-xs text-neutral-400">
          <span>Overall Unlocked</span>
          <span className="font-mono font-bold text-white">{percentage}%</span>
        </div>
        <div className="w-full bg-[#242424] h-3 rounded-full overflow-hidden p-0.5 border border-[#333]">
          <div
            className="bg-gradient-to-r from-amber-500 via-indigo-500 to-emerald-400 h-full rounded-full transition-all duration-500"
            style={{ width: `${percentage}%` }}
          />
        </div>
      </div>

      {/* Category Pills */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
        <div className="bg-[#242424] border border-[#333] rounded-xl p-3 flex items-center gap-3">
          <Flame className="w-4 h-4 text-amber-400 fill-amber-400" />
          <div>
            <span className="text-[10px] text-neutral-400 uppercase font-semibold">Streaks</span>
            <p className="text-xs font-bold text-white">{streakCount} Unlocked</p>
          </div>
        </div>

        <div className="bg-[#242424] border border-[#333] rounded-xl p-3 flex items-center gap-3">
          <Award className="w-4 h-4 text-emerald-400" />
          <div>
            <span className="text-[10px] text-neutral-400 uppercase font-semibold">Completions</span>
            <p className="text-xs font-bold text-white">{completionCount} Unlocked</p>
          </div>
        </div>

        <div className="bg-[#242424] border border-[#333] rounded-xl p-3 flex items-center gap-3">
          <Zap className="w-4 h-4 text-indigo-400" />
          <div>
            <span className="text-[10px] text-neutral-400 uppercase font-semibold">Habits</span>
            <p className="text-xs font-bold text-white">{habitCount} Unlocked</p>
          </div>
        </div>

        <div className="bg-[#242424] border border-[#333] rounded-xl p-3 flex items-center gap-3">
          <Trophy className="w-4 h-4 text-purple-400" />
          <div>
            <span className="text-[10px] text-neutral-400 uppercase font-semibold">Goals</span>
            <p className="text-xs font-bold text-white">{goalCount} Unlocked</p>
          </div>
        </div>
      </div>
    </div>
  );
}
