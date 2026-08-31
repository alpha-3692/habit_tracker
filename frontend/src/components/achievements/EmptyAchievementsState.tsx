"use client";

import { Trophy } from "lucide-react";

interface EmptyAchievementsStateProps {
  message?: string;
}

export function EmptyAchievementsState({
  message = "No achievements found for this filter.",
}: EmptyAchievementsStateProps) {
  return (
    <div className="text-center py-16 bg-[#1a1a1a] border border-[#2e2e2e] rounded-2xl p-8 space-y-3">
      <div className="w-12 h-12 rounded-2xl bg-[#242424] flex items-center justify-center text-neutral-400 mx-auto">
        <Trophy className="w-6 h-6 text-neutral-500" />
      </div>
      <div className="space-y-1">
        <h3 className="text-sm font-bold text-white">No Badges Here</h3>
        <p className="text-xs text-neutral-400">{message}</p>
      </div>
    </div>
  );
}
