"use client";

import { BellRing, Plus } from "lucide-react";

interface EmptyRemindersStateProps {
  onAddReminder: () => void;
  hasHabits: boolean;
}

export function EmptyRemindersState({
  onAddReminder,
  hasHabits,
}: EmptyRemindersStateProps) {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center rounded-3xl bg-[#141414] border border-[#242424] space-y-4">
      <div className="w-16 h-16 rounded-3xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
        <BellRing className="w-8 h-8" />
      </div>

      <div className="max-w-md space-y-1">
        <h3 className="text-base font-bold text-white tracking-tight">
          No Reminders Configured
        </h3>
        <p className="text-xs text-neutral-400">
          {hasHabits
            ? "Stay consistent with timely reminders for your daily habits and routines."
            : "Create your first habit before scheduling habit reminders."}
        </p>
      </div>

      {hasHabits && (
        <button
          onClick={onAddReminder}
          className="flex items-center gap-2 px-4 py-2.5 bg-amber-500 hover:bg-amber-400 text-black text-xs font-bold rounded-xl transition shadow-lg shadow-amber-500/20"
        >
          <Plus className="w-4 h-4" />
          <span>Add Reminder</span>
        </button>
      )}
    </div>
  );
}
