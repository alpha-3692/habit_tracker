"use client";

import { Reminder } from "@/types";
import { Bell, Clock, Calendar, Edit2, Trash2, Power } from "lucide-react";

interface ReminderCardProps {
  reminder: Reminder;
  onToggleActive: (reminder: Reminder) => void;
  onEdit: (reminder: Reminder) => void;
  onDelete: (id: string) => void;
}

const WEEKDAY_ABBR = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

export function ReminderCard({
  reminder,
  onToggleActive,
  onEdit,
  onDelete,
}: ReminderCardProps) {
  // Format reminder time to 12-hour format
  const formatTime = (timeStr: string) => {
    const [h, m] = timeStr.split(":");
    const hour = parseInt(h, 10);
    const ampm = hour >= 12 ? "PM" : "AM";
    const formattedHour = hour % 12 || 12;
    return `${formattedHour}:${m} ${ampm}`;
  };

  const getDaysLabel = (days: number[] | null) => {
    if (!days || days.length === 0 || days.length === 7) return "Every Scheduled Day";
    if (days.length === 5 && !days.includes(5) && !days.includes(6)) return "Weekdays (Mon–Fri)";
    if (days.length === 2 && days.includes(5) && days.includes(6)) return "Weekends (Sat–Sun)";
    return days.map((d) => WEEKDAY_ABBR[d]).join(", ");
  };

  return (
    <div
      className={`rounded-2xl p-5 border transition flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-lg ${
        reminder.is_active
          ? "bg-[#1a1a1a] border-[#2e2e2e] hover:border-[#3e3e3e]"
          : "bg-[#151515] border-[#242424] opacity-60"
      }`}
    >
      <div className="flex items-start gap-4">
        {/* Bell Icon Badge */}
        <div
          className={`w-12 h-12 rounded-2xl flex items-center justify-center flex-shrink-0 border ${
            reminder.is_active
              ? "bg-amber-500/10 border-amber-500/30 text-amber-400"
              : "bg-[#242424] border-[#333] text-neutral-500"
          }`}
        >
          <Bell className={`w-6 h-6 ${reminder.is_active ? "fill-amber-400/20" : ""}`} />
        </div>

        {/* Info */}
        <div className="space-y-1">
          <div className="flex items-center gap-2 flex-wrap">
            <h3 className="text-base font-bold text-white tracking-tight">
              {reminder.habit_title || "Untitled Habit"}
            </h3>
            {reminder.habit_category && (
              <span className="px-2 py-0.5 rounded-md bg-[#242424] text-neutral-400 text-[10px] font-semibold uppercase tracking-wider">
                {reminder.habit_category}
              </span>
            )}
          </div>

          <div className="flex items-center gap-3 text-xs text-neutral-400 flex-wrap">
            <div className="flex items-center gap-1.5 text-amber-300 font-semibold">
              <Clock className="w-3.5 h-3.5" />
              <span>{formatTime(reminder.reminder_time)}</span>
            </div>
            <span>•</span>
            <div className="flex items-center gap-1.5 text-neutral-300">
              <Calendar className="w-3.5 h-3.5 text-neutral-400" />
              <span>{getDaysLabel(reminder.days_of_week)}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2 self-end md:self-auto flex-shrink-0">
        <button
          onClick={() => onToggleActive(reminder)}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold border transition ${
            reminder.is_active
              ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/20"
              : "bg-[#242424] border-[#333] text-neutral-400 hover:text-white"
          }`}
          title={reminder.is_active ? "Disable reminder" : "Enable reminder"}
        >
          <Power className="w-3.5 h-3.5" />
          <span>{reminder.is_active ? "Active" : "Disabled"}</span>
        </button>

        <button
          onClick={() => onEdit(reminder)}
          className="p-2 text-neutral-400 hover:text-white hover:bg-[#242424] rounded-xl border border-[#333] transition"
          title="Edit reminder"
        >
          <Edit2 className="w-3.5 h-3.5" />
        </button>

        <button
          onClick={() => onDelete(reminder.id)}
          className="p-2 text-neutral-400 hover:text-red-400 hover:bg-red-500/10 rounded-xl border border-[#333] transition"
          title="Delete reminder"
        >
          <Trash2 className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
}
