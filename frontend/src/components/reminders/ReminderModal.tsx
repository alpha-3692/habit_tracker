"use client";

import { useState, useEffect } from "react";
import { Habit, Reminder, CreateReminderPayload, UpdateReminderPayload } from "@/types";
import { X, Clock, Bell, Calendar, Sparkles } from "lucide-react";

interface ReminderModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (payload: CreateReminderPayload | UpdateReminderPayload) => Promise<void>;
  habits: Habit[];
  editingReminder?: Reminder | null;
}

const WEEKDAYS = [
  { id: 0, label: "Mon" },
  { id: 1, label: "Tue" },
  { id: 2, label: "Wed" },
  { id: 3, label: "Thu" },
  { id: 4, label: "Fri" },
  { id: 5, label: "Sat" },
  { id: 6, label: "Sun" },
];

export function ReminderModal({
  isOpen,
  onClose,
  onSave,
  habits,
  editingReminder,
}: ReminderModalProps) {
  const [habitId, setHabitId] = useState<string>("");
  const [reminderTime, setReminderTime] = useState<string>("08:00");
  const [selectedDays, setSelectedDays] = useState<number[]>([]);
  const [isActive, setIsActive] = useState<boolean>(true);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (editingReminder) {
      setHabitId(editingReminder.habit_id);
      setReminderTime(editingReminder.reminder_time.slice(0, 5));
      setSelectedDays(editingReminder.days_of_week || []);
      setIsActive(editingReminder.is_active);
    } else {
      setHabitId(habits[0]?.id || "");
      setReminderTime("08:00");
      setSelectedDays([]);
      setIsActive(true);
    }
    setError(null);
  }, [editingReminder, habits, isOpen]);

  if (!isOpen) return null;

  const toggleDay = (dayId: number) => {
    setSelectedDays((prev) =>
      prev.includes(dayId) ? prev.filter((d) => d !== dayId) : [...prev, dayId].sort()
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!habitId) {
      setError("Please select a habit.");
      return;
    }
    if (!reminderTime) {
      setError("Please specify a reminder time.");
      return;
    }

    try {
      setIsSubmitting(true);
      setError(null);

      const payload: CreateReminderPayload = {
        habit_id: habitId,
        reminder_time: reminderTime.length === 5 ? `${reminderTime}:00` : reminderTime,
        days_of_week: selectedDays.length > 0 ? selectedDays : null,
        is_active: isActive,
      };

      await onSave(payload);
      onClose();
    } catch (err: any) {
      setError(err?.message || "Failed to save reminder.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fade-in">
      <div className="bg-[#1a1a1a] border border-[#2e2e2e] rounded-3xl w-full max-w-lg p-6 shadow-2xl space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-[#2e2e2e] pb-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400">
              <Bell className="w-4 h-4" />
            </div>
            <h2 className="text-lg font-bold text-white tracking-tight">
              {editingReminder ? "Edit Habit Reminder" : "Add Habit Reminder"}
            </h2>
          </div>
          <button
            onClick={onClose}
            className="text-neutral-400 hover:text-white p-1 rounded-lg hover:bg-[#242424] transition"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {error && (
          <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-xl text-xs text-red-400">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Habit Selector */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-neutral-300">
              Select Habit
            </label>
            <select
              value={habitId}
              onChange={(e) => setHabitId(e.target.value)}
              disabled={!!editingReminder}
              className="w-full bg-[#242424] border border-[#333] focus:border-amber-500 rounded-xl px-3.5 py-2.5 text-xs text-white outline-none transition disabled:opacity-60"
            >
              {habits.map((h) => (
                <option key={h.id} value={h.id}>
                  {h.title} ({h.category})
                </option>
              ))}
            </select>
          </div>

          {/* Time Picker */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-neutral-300">
              Reminder Time
            </label>
            <div className="relative">
              <input
                type="time"
                value={reminderTime}
                onChange={(e) => setReminderTime(e.target.value)}
                required
                className="w-full bg-[#242424] border border-[#333] focus:border-amber-500 rounded-xl px-3.5 py-2.5 text-xs text-white outline-none transition font-mono"
              />
            </div>
          </div>

          {/* Days of Week */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-xs font-semibold text-neutral-300">
                Reminder Days
              </label>
              <span className="text-[11px] text-neutral-500">
                {selectedDays.length === 0 ? "Every scheduled day" : `${selectedDays.length} days selected`}
              </span>
            </div>

            <div className="grid grid-cols-7 gap-1.5">
              {WEEKDAYS.map((day) => {
                const isSelected = selectedDays.includes(day.id);
                return (
                  <button
                    key={day.id}
                    type="button"
                    onClick={() => toggleDay(day.id)}
                    className={`py-2 text-xs font-semibold rounded-xl border transition ${
                      isSelected
                        ? "bg-amber-500/20 border-amber-500/40 text-amber-300"
                        : "bg-[#242424] border-[#333] text-neutral-400 hover:text-white"
                    }`}
                  >
                    {day.label}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Active Switch Toggle */}
          <div className="flex items-center justify-between p-3 bg-[#242424] border border-[#333] rounded-xl">
            <span className="text-xs font-semibold text-neutral-300">
              Enable Reminder
            </span>
            <input
              type="checkbox"
              checked={isActive}
              onChange={(e) => setIsActive(e.target.checked)}
              className="w-4 h-4 accent-amber-500 rounded cursor-pointer"
            />
          </div>

          {/* Submit Buttons */}
          <div className="flex items-center justify-end gap-2.5 pt-4 border-t border-[#2e2e2e]">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 bg-[#242424] hover:bg-[#2e2e2e] text-xs font-semibold text-white rounded-xl border border-[#333] transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-5 py-2 bg-amber-500 hover:bg-amber-400 text-black text-xs font-bold rounded-xl shadow-lg shadow-amber-500/20 transition disabled:opacity-50"
            >
              {isSubmitting ? "Saving..." : editingReminder ? "Save Changes" : "Create Reminder"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
