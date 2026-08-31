"use client";

import { AchievementWithProgress } from "@/types";
import {
  Flame,
  CheckCircle2,
  Award,
  Crown,
  PlusCircle,
  Layers,
  Zap,
  Target,
  Flag,
  Trophy,
  Lock,
} from "lucide-react";

interface AchievementCardProps {
  achievement: AchievementWithProgress;
}

export function AchievementCard({ achievement }: AchievementCardProps) {
  const getIcon = (iconName: string | null, isUnlocked: boolean) => {
    const size = "w-6 h-6";
    const colorClass = isUnlocked ? "text-amber-400" : "text-neutral-500";

    switch (iconName) {
      case "flame":
        return <Flame className={`${size} ${colorClass} ${isUnlocked ? "fill-amber-400" : ""}`} />;
      case "check-circle":
        return <CheckCircle2 className={`${size} ${isUnlocked ? "text-emerald-400" : "text-neutral-500"}`} />;
      case "award":
        return <Award className={`${size} ${isUnlocked ? "text-indigo-400" : "text-neutral-500"}`} />;
      case "crown":
        return <Crown className={`${size} ${isUnlocked ? "text-amber-300" : "text-neutral-500"}`} />;
      case "plus-circle":
        return <PlusCircle className={`${size} ${isUnlocked ? "text-emerald-400" : "text-neutral-500"}`} />;
      case "layers":
        return <Layers className={`${size} ${isUnlocked ? "text-indigo-400" : "text-neutral-500"}`} />;
      case "zap":
        return <Zap className={`${size} ${isUnlocked ? "text-amber-400 fill-amber-400" : "text-neutral-500"}`} />;
      case "target":
        return <Target className={`${size} ${isUnlocked ? "text-indigo-400" : "text-neutral-500"}`} />;
      case "flag":
        return <Flag className={`${size} ${isUnlocked ? "text-emerald-400" : "text-neutral-500"}`} />;
      case "trophy":
        return <Trophy className={`${size} ${isUnlocked ? "text-amber-400 fill-amber-400" : "text-neutral-500"}`} />;
      default:
        return <Award className={`${size} ${colorClass}`} />;
    }
  };

  const unlockedDateStr = achievement.unlocked_at
    ? new Date(achievement.unlocked_at).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
      })
    : null;

  return (
    <div
      className={`rounded-2xl p-5 border transition flex flex-col justify-between space-y-4 shadow-lg ${
        achievement.is_unlocked
          ? "bg-[#1f1a14] border-amber-500/30 hover:border-amber-500/50 shadow-amber-500/5"
          : "bg-[#181818] border-[#2e2e2e] opacity-80"
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        {/* Badge Icon */}
        <div
          className={`w-12 h-12 rounded-2xl flex items-center justify-center flex-shrink-0 border ${
            achievement.is_unlocked
              ? "bg-amber-500/10 border-amber-500/30"
              : "bg-[#242424] border-[#333]"
          }`}
        >
          {getIcon(achievement.icon, achievement.is_unlocked)}
        </div>

        {/* Category & Status Badges */}
        <div className="flex items-center gap-1.5 flex-wrap justify-end">
          <span className="px-2 py-0.5 rounded-md bg-[#242424] text-neutral-400 text-[10px] font-semibold uppercase tracking-wider">
            {achievement.category}
          </span>
          {achievement.is_unlocked ? (
            <span className="px-2 py-0.5 rounded-md bg-amber-500/20 text-amber-400 text-[10px] font-bold uppercase tracking-wider">
              Unlocked
            </span>
          ) : (
            <span className="px-2 py-0.5 rounded-md bg-[#242424] text-neutral-500 text-[10px] font-semibold flex items-center gap-1">
              <Lock className="w-2.5 h-2.5" /> Locked
            </span>
          )}
        </div>
      </div>

      {/* Title & Description */}
      <div className="space-y-1">
        <h3
          className={`text-base font-bold tracking-tight ${
            achievement.is_unlocked ? "text-amber-100" : "text-neutral-300"
          }`}
        >
          {achievement.title}
        </h3>
        <p className="text-xs text-neutral-400 leading-relaxed">
          {achievement.description}
        </p>
      </div>

      {/* Progress Footer */}
      <div className="pt-2 border-t border-[#2e2e2e]/60 space-y-2">
        <div className="flex items-center justify-between text-xs">
          <span className="text-neutral-400">
            {achievement.is_unlocked ? (
              <span className="text-[11px] text-amber-400/90 font-medium">
                Unlocked {unlockedDateStr}
              </span>
            ) : (
              <span>
                Progress: {achievement.progress} / {achievement.target}
              </span>
            )}
          </span>
          <span className="font-mono text-neutral-400 font-semibold">
            {achievement.progress_percentage}%
          </span>
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-[#141414] h-1.5 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 ${
              achievement.is_unlocked
                ? "bg-amber-400"
                : achievement.progress_percentage > 0
                ? "bg-indigo-500"
                : "bg-neutral-800"
            }`}
            style={{ width: `${achievement.progress_percentage}%` }}
          />
        </div>
      </div>
    </div>
  );
}
