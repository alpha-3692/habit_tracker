"use client";

import { Zap, TrendingUp, Target, Activity } from "lucide-react";

interface MomentumScoreCardProps {
  score: number;
  overallConsistency: number;
  totalHabits: number;
  totalCompletions: number;
}

export function MomentumScoreCard({
  score,
  overallConsistency,
  totalHabits,
  totalCompletions,
}: MomentumScoreCardProps) {
  const getScoreStatus = (s: number) => {
    if (s >= 80) return { label: "Peak Lock-In", color: "text-emerald-400", bg: "bg-emerald-500/10 border-emerald-500/20" };
    if (s >= 60) return { label: "Strong Momentum", color: "text-indigo-400", bg: "bg-indigo-500/10 border-indigo-500/20" };
    if (s >= 40) return { label: "Building Rhythm", color: "text-amber-400", bg: "bg-amber-500/10 border-amber-500/20" };
    return { label: "Starting Up", color: "text-neutral-400", bg: "bg-neutral-800 border-neutral-700" };
  };

  const status = getScoreStatus(score);

  return (
    <div className="bg-[#1a1a1a] border border-[#2e2e2e] rounded-2xl p-6 shadow-xl space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Zap className="w-5 h-5 text-amber-400 fill-amber-400" />
            <h2 className="text-xl font-extrabold text-white tracking-tight">
              Execution Momentum
            </h2>
          </div>
          <p className="text-xs text-neutral-400">
            Weighted composite of your 7-day velocity, 30-day consistency, and active streaks.
          </p>
        </div>

        <div className={`px-3 py-1.5 rounded-xl border text-xs font-bold ${status.bg} ${status.color} self-start sm:self-auto`}>
          {status.label}
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 pt-2">
        {/* Momentum Score Gauge */}
        <div className="bg-[#242424] border border-[#333] rounded-xl p-4 flex flex-col justify-between space-y-2">
          <span className="text-[11px] font-semibold text-neutral-400 uppercase tracking-wider">
            Momentum Score
          </span>
          <div className="flex items-baseline gap-2">
            <span className="text-4xl font-extrabold text-white tracking-tight">{score}</span>
            <span className="text-xs text-neutral-500 font-mono">/ 100</span>
          </div>
          <div className="w-full bg-[#161616] h-2 rounded-full overflow-hidden p-0.5">
            <div
              className="bg-gradient-to-r from-amber-500 via-indigo-500 to-emerald-400 h-full rounded-full transition-all duration-500"
              style={{ width: `${score}%` }}
            />
          </div>
        </div>

        {/* Overall Consistency */}
        <div className="bg-[#242424] border border-[#333] rounded-xl p-4 space-y-2">
          <span className="text-[11px] font-semibold text-neutral-400 uppercase tracking-wider">
            Overall Consistency
          </span>
          <p className="text-3xl font-extrabold text-emerald-400">{overallConsistency}%</p>
          <p className="text-[11px] text-neutral-400">Across all scheduled days</p>
        </div>

        {/* Total Habits */}
        <div className="bg-[#242424] border border-[#333] rounded-xl p-4 space-y-2">
          <span className="text-[11px] font-semibold text-neutral-400 uppercase tracking-wider">
            Active Habits
          </span>
          <p className="text-3xl font-extrabold text-white">{totalHabits}</p>
          <p className="text-[11px] text-neutral-400">Tracked in this period</p>
        </div>

        {/* Total Completions */}
        <div className="bg-[#242424] border border-[#333] rounded-xl p-4 space-y-2">
          <span className="text-[11px] font-semibold text-neutral-400 uppercase tracking-wider">
            Total Completions
          </span>
          <p className="text-3xl font-extrabold text-white">{totalCompletions}</p>
          <p className="text-[11px] text-neutral-400">Logged executions</p>
        </div>
      </div>
    </div>
  );
}
