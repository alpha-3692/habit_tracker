"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import { Reminder, Habit, CreateReminderPayload, UpdateReminderPayload } from "@/types";
import { remindersApi } from "@/lib/api/reminders";
import { habitsApi } from "@/lib/api/habits";
import { DashboardHeader } from "@/components/dashboard/DashboardHeader";
import { ReminderList } from "@/components/reminders/ReminderList";
import { ReminderModal } from "@/components/reminders/ReminderModal";
import { Bell, Plus, Filter, AlertCircle, RefreshCw } from "lucide-react";

export default function RemindersPage() {
  const router = useRouter();
  const { user, accessToken, isLoading, logout } = useAuth();

  const [reminders, setReminders] = useState<Reminder[]>([]);
  const [habits, setHabits] = useState<Habit[]>([]);
  const [isFetching, setIsFetching] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [editingReminder, setEditingReminder] = useState<Reminder | null>(null);
  const [activeFilter, setActiveFilter] = useState<"all" | "active" | "disabled">("all");

  const fetchData = async () => {
    if (!accessToken) return;
    try {
      setIsFetching(true);
      setError(null);
      const [remList, habitList] = await Promise.all([
        remindersApi.getReminders(accessToken),
        habitsApi.getHabits(accessToken),
      ]);
      setReminders(remList);
      setHabits(habitList.filter((h) => !h.is_archived));
    } catch (err: any) {
      setError(err?.message || "Failed to load reminders data.");
    } finally {
      setIsFetching(false);
    }
  };

  useEffect(() => {
    if (!isLoading && !user) {
      router.push("/login");
      return;
    }
    if (accessToken) {
      fetchData();
    }
  }, [isLoading, user, accessToken]);

  const handleCreateOrUpdate = async (
    payload: CreateReminderPayload | UpdateReminderPayload
  ) => {
    if (!accessToken) return;
    if (editingReminder) {
      const updated = await remindersApi.updateReminder(
        accessToken,
        editingReminder.id,
        payload as UpdateReminderPayload
      );
      setReminders((prev) =>
        prev.map((r) => (r.id === updated.id ? updated : r))
      );
    } else {
      const created = await remindersApi.createReminder(
        accessToken,
        payload as CreateReminderPayload
      );
      setReminders((prev) => [created, ...prev]);
    }
    setIsModalOpen(false);
    setEditingReminder(null);
  };

  const handleToggleActive = async (reminder: Reminder) => {
    if (!accessToken) return;
    try {
      const updated = await remindersApi.updateReminder(
        accessToken,
        reminder.id,
        { is_active: !reminder.is_active }
      );
      setReminders((prev) =>
        prev.map((r) => (r.id === updated.id ? updated : r))
      );
    } catch (err: any) {
      setError(err?.message || "Failed to toggle reminder status.");
    }
  };

  const handleDelete = async (id: string) => {
    if (!accessToken) return;
    try {
      await remindersApi.deleteReminder(accessToken, id);
      setReminders((prev) => prev.filter((r) => r.id !== id));
    } catch (err: any) {
      setError(err?.message || "Failed to delete reminder.");
    }
  };

  if (isLoading || isFetching) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#0f0f0f] text-neutral-400">
        <p className="animate-pulse text-sm font-medium">Loading Reminders...</p>
      </div>
    );
  }

  if (!user) return null;

  const filteredReminders = reminders.filter((r) => {
    if (activeFilter === "active") return r.is_active;
    if (activeFilter === "disabled") return !r.is_active;
    return true;
  });

  return (
    <main className="min-h-screen bg-[#0f0f0f] text-white p-6 max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <DashboardHeader
        fullName={user.full_name}
        currentDateStr={user.created_at ? new Date().toISOString().split("T")[0] : ""}
        timezone={user.timezone}
        onLogout={() => {
          logout();
          router.push("/login");
        }}
      />

      {/* Page Title & Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400">
              <Bell className="w-4 h-4" />
            </div>
            <h1 className="text-xl font-bold tracking-tight text-white">
              Habit Reminders
            </h1>
          </div>
          <p className="text-xs text-neutral-400 mt-1">
            Configure timezone-aware reminders for your daily habits and routines.
          </p>
        </div>

        <button
          onClick={() => {
            setEditingReminder(null);
            setIsModalOpen(true);
          }}
          disabled={habits.length === 0}
          className="flex items-center gap-2 px-4 py-2 bg-amber-500 hover:bg-amber-400 text-black text-xs font-bold rounded-xl transition shadow-lg shadow-amber-500/20 disabled:opacity-50"
        >
          <Plus className="w-4 h-4" />
          <span>Add Reminder</span>
        </button>
      </div>

      {/* Error Callout */}
      {error && (
        <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-xs flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
          <button onClick={() => setError(null)} className="text-red-400 hover:text-white">
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Filters */}
      {reminders.length > 0 && (
        <div className="flex items-center gap-1.5 p-1 bg-[#1a1a1a] border border-[#2e2e2e] rounded-xl w-fit">
          <button
            onClick={() => setActiveFilter("all")}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
              activeFilter === "all"
                ? "bg-[#282828] text-white shadow-sm"
                : "text-neutral-400 hover:text-white"
            }`}
          >
            All ({reminders.length})
          </button>
          <button
            onClick={() => setActiveFilter("active")}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
              activeFilter === "active"
                ? "bg-[#282828] text-white shadow-sm"
                : "text-neutral-400 hover:text-white"
            }`}
          >
            Active ({reminders.filter((r) => r.is_active).length})
          </button>
          <button
            onClick={() => setActiveFilter("disabled")}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
              activeFilter === "disabled"
                ? "bg-[#282828] text-white shadow-sm"
                : "text-neutral-400 hover:text-white"
            }`}
          >
            Disabled ({reminders.filter((r) => !r.is_active).length})
          </button>
        </div>
      )}

      {/* Reminders List */}
      <ReminderList
        reminders={filteredReminders}
        onToggleActive={handleToggleActive}
        onEdit={(r) => {
          setEditingReminder(r);
          setIsModalOpen(true);
        }}
        onDelete={handleDelete}
        onAddReminder={() => {
          setEditingReminder(null);
          setIsModalOpen(true);
        }}
        hasHabits={habits.length > 0}
      />

      {/* Reminder Modal */}
      <ReminderModal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setEditingReminder(null);
        }}
        onSave={handleCreateOrUpdate}
        habits={habits}
        editingReminder={editingReminder}
      />
    </main>
  );
}
