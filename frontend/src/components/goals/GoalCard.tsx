"use client";

import { useState } from "react";
import { Goal } from "@/types";
import {
  Calendar,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  Edit2,
  Flame,
  Layers,
  Trash2,
} from "lucide-react";

interface GoalCardProps {
  goal: Goal;
  onEdit: (goal: Goal) => void;
  onDelete: (goalId: string) => void;
  onToggleStatus: (goal: Goal) => void;
}

export function GoalCard({
  goal,
  onEdit,
  onDelete,
  onToggleStatus,
}: GoalCardProps) {
  const [isExpanded, setIsExpanded] = useState<boolean>(false);
  const isCompleted = goal.status === "completed";

  const formattedTargetDate = goal.target_date
    ? new Date(goal.target_date).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
      })
    : null;

  return (
    <div className="bg-[#1a1a1a] border border-[#2e2e2e] hover:border-[#3e3e3e] rounded-2xl p-5 shadow-lg space-y-4 transition">
      {/* Top row: Category, Status, Actions */}
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="px-2 py-0.5 rounded-md bg-[#242424] text-neutral-400 text-[10px] font-semibold uppercase tracking-wider">
            {goal.category}
          </span>
          <span
            className={`px-2 py-0.5 rounded-md text-[10px] font-semibold uppercase tracking-wider ${
              isCompleted
                ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                : "bg-indigo-500/10 text-indigo-400 border border-indigo-500/20"
            }`}
          >
            {goal.status}
          </span>
        </div>

        <div className="flex items-center gap-1">
          <button
            onClick={() => onToggleStatus(goal)}
            className={`p-1.5 rounded-lg border text-xs transition ${
              isCompleted
                ? "text-emerald-400 border-emerald-500/20 hover:bg-emerald-500/10"
                : "text-neutral-400 border-[#333] hover:text-white hover:bg-[#242424]"
            }`}
            title={isCompleted ? "Mark Active" : "Mark Completed"}
          >
            <CheckCircle2 className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => onEdit(goal)}
            className="p-1.5 text-neutral-400 hover:text-white hover:bg-[#242424] rounded-lg border border-[#333] transition"
            title="Edit Goal"
          >
            <Edit2 className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => onDelete(goal.id)}
            className="p-1.5 text-neutral-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg border border-[#333] transition"
            title="Delete Goal"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Goal Title & Description */}
      <div className="space-y-1">
        <h3
          className={`text-base font-bold tracking-tight ${
            isCompleted ? "line-through text-neutral-400" : "text-white"
          }`}
        >
          {goal.title}
        </h3>
        {goal.description && (
          <p className="text-xs text-neutral-400 leading-relaxed">
            {goal.description}
          </p>
        )}
      </div>

      {/* Progress Bar */}
      <div className="space-y-1.5">
        <div className="flex items-center justify-between text-xs font-semibold">
          <span className="text-neutral-400">Progress</span>
          <span className="text-white font-mono">{goal.progress_percentage}%</span>
        </div>
        <div className="w-full bg-[#242424] h-2.5 rounded-full overflow-hidden p-0.5 border border-[#333]">
          <div
            className={`h-full rounded-full transition-all duration-500 ${
              isCompleted
                ? "bg-emerald-400"
                : "bg-gradient-to-r from-indigo-500 to-emerald-400"
            }`}
            style={{ width: `${Math.min(100, Math.max(0, goal.progress_percentage))}%` }}
          />
        </div>
      </div>

      {/* Metadata Row: Deadline & Associated Habits */}
      <div className="flex items-center justify-between pt-2 border-t border-[#2e2e2e] text-xs text-neutral-400">
        <div className="flex items-center gap-1.5">
          <Layers className="w-3.5 h-3.5 text-indigo-400" />
          <span>
            {goal.habit_count} {goal.habit_count === 1 ? "habit" : "habits"} linked
          </span>
        </div>

        {formattedTargetDate && (
          <div className="flex items-center gap-1.5">
            <Calendar className="w-3.5 h-3.5 text-neutral-500" />
            <span>Target: {formattedTargetDate}</span>
          </div>
        )}
      </div>

      {/* Expand Contributing Habits */}
      {goal.habits && goal.habits.length > 0 && (
        <div className="space-y-2 pt-1">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="flex items-center justify-between w-full text-xs font-semibold text-neutral-400 hover:text-white transition py-1"
          >
            <span>Contributing Habits ({goal.habits.length})</span>
            {isExpanded ? (
              <ChevronUp className="w-3.5 h-3.5" />
            ) : (
              <ChevronDown className="w-3.5 h-3.5" />
            )}
          </button>

          {isExpanded && (
            <div className="space-y-1.5 pl-2 border-l-2 border-indigo-500/30">
              {goal.habits.map((h) => (
                <div
                  key={h.id}
                  className="flex items-center justify-between text-xs bg-[#242424] px-3 py-2 rounded-xl"
                >
                  <span className="font-medium text-white truncate max-w-[200px]">
                    {h.title}
                  </span>
                  <div className="flex items-center gap-3 text-neutral-400 font-mono text-[11px]">
                    <div className="flex items-center gap-1 text-amber-400 font-bold">
                      <Flame className="w-3 h-3 text-amber-500 fill-amber-500" />
                      <span>{h.current_streak}d</span>
                    </div>
                    <span>{h.completion_percentage}%</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
