"use client";

import { useState } from "react";
import { AchievementWithProgress } from "@/types";
import { AchievementCard } from "./AchievementCard";
import { EmptyAchievementsState } from "./EmptyAchievementsState";

interface AchievementGridProps {
  achievements: AchievementWithProgress[];
}

export function AchievementGrid({ achievements }: AchievementGridProps) {
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [statusFilter, setStatusFilter] = useState<"all" | "unlocked" | "locked">("all");

  const categories = [
    { id: "all", label: "All Categories" },
    { id: "streak", label: "Streaks" },
    { id: "completion", label: "Completions" },
    { id: "habit", label: "Habits" },
    { id: "goal", label: "Goals" },
  ];

  const filtered = achievements.filter((a) => {
    const matchesCategory =
      selectedCategory === "all" || a.category === selectedCategory;
    const matchesStatus =
      statusFilter === "all" ||
      (statusFilter === "unlocked" && a.is_unlocked) ||
      (statusFilter === "locked" && !a.is_unlocked);

    return matchesCategory && matchesStatus;
  });

  return (
    <div className="space-y-6">
      {/* Category & Status Filter Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#2e2e2e] pb-4">
        {/* Category Tabs */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0">
          {categories.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(cat.id)}
              className={`px-3 py-1.5 text-xs font-semibold rounded-xl whitespace-nowrap transition ${
                selectedCategory === cat.id
                  ? "bg-amber-500/20 text-amber-300 border border-amber-500/30"
                  : "text-neutral-400 hover:text-white bg-[#242424] border border-[#333]"
              }`}
            >
              {cat.label}
            </button>
          ))}
        </div>

        {/* Status Toggle (All / Unlocked / Locked) */}
        <div className="flex items-center gap-1 bg-[#1a1a1a] p-1 rounded-xl border border-[#333] self-start sm:self-auto">
          <button
            onClick={() => setStatusFilter("all")}
            className={`px-2.5 py-1 text-[11px] font-semibold rounded-lg transition ${
              statusFilter === "all"
                ? "bg-[#2e2e2e] text-white"
                : "text-neutral-400 hover:text-white"
            }`}
          >
            All
          </button>
          <button
            onClick={() => setStatusFilter("unlocked")}
            className={`px-2.5 py-1 text-[11px] font-semibold rounded-lg transition ${
              statusFilter === "unlocked"
                ? "bg-amber-500/20 text-amber-300"
                : "text-neutral-400 hover:text-white"
            }`}
          >
            Unlocked
          </button>
          <button
            onClick={() => setStatusFilter("locked")}
            className={`px-2.5 py-1 text-[11px] font-semibold rounded-lg transition ${
              statusFilter === "locked"
                ? "bg-[#2e2e2e] text-white"
                : "text-neutral-400 hover:text-white"
            }`}
          >
            Locked
          </button>
        </div>
      </div>

      {/* Grid */}
      {filtered.length === 0 ? (
        <EmptyAchievementsState message="Try changing your category or unlock status filter." />
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((ach) => (
            <AchievementCard key={ach.id} achievement={ach} />
          ))}
        </div>
      )}
    </div>
  );
}
