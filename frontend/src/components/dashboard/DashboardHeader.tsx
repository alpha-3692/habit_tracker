"use client";

import Link from "next/link";
import { LogOut, Plus, Target, Calendar, BarChart2, Trophy, Bell } from "lucide-react";

interface DashboardHeaderProps {
  fullName: string | null;
  currentDateStr: string;
  timezone: string;
  onLogout: () => void;
}

export function DashboardHeader({
  fullName,
  currentDateStr,
  timezone,
  onLogout,
}: DashboardHeaderProps) {
  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return "Good morning";
    if (hour < 18) return "Good afternoon";
    return "Good evening";
  };

  const formattedDate = new Date(currentDateStr).toLocaleDateString("en-US", {
    weekday: "long",
    month: "long",
    day: "numeric",
    year: "numeric",
  });

  return (
    <header className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#2e2e2e] pb-6">
      <div className="space-y-1">
        <div className="flex items-center gap-2">
          <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
            {getGreeting()}, {fullName || "Builder"} 👋
          </h1>
        </div>
        <div className="flex items-center gap-2 text-xs text-neutral-400">
          <span>{formattedDate}</span>
          <span>•</span>
          <span className="font-mono text-neutral-500">{timezone}</span>
        </div>
      </div>

      <div className="flex items-center gap-2 flex-wrap">
        <Link
          href="/calendar"
          className="flex items-center gap-1.5 px-3 py-2 bg-[#242424] hover:bg-[#2e2e2e] text-white text-xs font-semibold rounded-xl border border-[#333] transition"
        >
          <Calendar className="w-3.5 h-3.5 text-emerald-400" />
          <span>Calendar</span>
        </Link>

        <Link
          href="/analytics"
          className="flex items-center gap-1.5 px-3 py-2 bg-[#242424] hover:bg-[#2e2e2e] text-white text-xs font-semibold rounded-xl border border-[#333] transition"
        >
          <BarChart2 className="w-3.5 h-3.5 text-indigo-400" />
          <span>Analytics</span>
        </Link>

        <Link
          href="/achievements"
          className="flex items-center gap-1.5 px-3 py-2 bg-[#242424] hover:bg-[#2e2e2e] text-white text-xs font-semibold rounded-xl border border-[#333] transition"
        >
          <Trophy className="w-3.5 h-3.5 text-amber-400" />
          <span>Badges</span>
        </Link>

        <Link
          href="/reminders"
          className="flex items-center gap-1.5 px-3 py-2 bg-[#242424] hover:bg-[#2e2e2e] text-white text-xs font-semibold rounded-xl border border-[#333] transition"
        >
          <Bell className="w-3.5 h-3.5 text-amber-400" />
          <span>Reminders</span>
        </Link>

        <Link
          href="/goals"
          className="flex items-center gap-1.5 px-3 py-2 bg-[#242424] hover:bg-[#2e2e2e] text-white text-xs font-semibold rounded-xl border border-[#333] transition"
        >
          <Target className="w-3.5 h-3.5 text-purple-400" />
          <span>Goals</span>
        </Link>

        <Link
          href="/habits"
          className="flex items-center gap-1.5 px-3 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-xl shadow-lg shadow-indigo-600/20 transition"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>Habits</span>
        </Link>

        <button
          onClick={onLogout}
          className="p-2 text-neutral-400 hover:text-white hover:bg-[#242424] rounded-xl border border-[#333] transition"
          title="Sign out"
        >
          <LogOut className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
}
