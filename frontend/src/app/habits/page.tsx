"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/context/AuthContext";
import { Habit, Goal } from "@/types";
import { habitsApi, CreateHabitPayload } from "@/lib/api/habits";
import { goalsApi } from "@/lib/api/goals";
import {
  Plus,
  Flame,
  CheckCircle2,
  Archive,
  Trash2,
  Edit2,
  Sparkles,
  AlertCircle,
  X,
  RotateCcw,
  LogOut,
  Target,
  ArrowLeft,
  Activity,
} from "lucide-react";

export default function HabitsPage() {
  const router = useRouter();
  const { user, accessToken, isLoading, logout } = useAuth();

  const [habits, setHabits] = useState<Habit[]>([]);
  const [goals, setGoals] = useState<Goal[]>([]);
  const [activeTab, setActiveTab] = useState<"active" | "archived">("active");
  const [isFetching, setIsFetching] = useState(true);

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingHabit, setEditingHabit] = useState<Habit | null>(null);

  // Form State
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("fitness");
  const [frequencyType, setFrequencyType] = useState("daily");
  const [targetValue, setTargetValue] = useState<number | "">("");
  const [targetUnit, setTargetUnit] = useState("");
  const [goalId, setGoalId] = useState<string>("");

  const [error, setError] = useState<string | null>(null);
  const [actionLoadingId, setActionLoadingId] = useState<string | null>(null);

  const fetchHabitsAndGoals = async () => {
    if (!accessToken) return;
    try {
      setIsFetching(true);
      const [habitsData, goalsData] = await Promise.all([
        habitsApi.getHabits(accessToken, {
          is_archived: activeTab === "archived",
        }),
        goalsApi.getGoals(accessToken, "active"),
      ]);
      setHabits(habitsData);
      setGoals(goalsData);
    } catch (err: any) {
      setError(err?.message || "Failed to load habits.");
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
      fetchHabitsAndGoals();
    }
  }, [isLoading, user, accessToken, activeTab]);

  const resetForm = () => {
    setTitle("");
    setDescription("");
    setCategory("fitness");
    setFrequencyType("daily");
    setTargetValue("");
    setTargetUnit("");
    setGoalId("");
    setEditingHabit(null);
    setError(null);
  };

  const handleOpenCreateModal = () => {
    resetForm();
    setIsModalOpen(true);
  };

  const handleOpenEditModal = (habit: Habit) => {
    setEditingHabit(habit);
    setTitle(habit.title);
    setDescription(habit.description || "");
    setCategory(habit.category);
    setFrequencyType(habit.frequency_type);
    setTargetValue(habit.target_value ?? "");
    setTargetUnit(habit.target_unit || "");
    setGoalId(habit.goal_id || "");
    setError(null);
    setIsModalOpen(true);
  };

  const handleSaveHabit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!accessToken) return;
    setError(null);

    const payload: CreateHabitPayload = {
      title,
      description: description || undefined,
      category,
      frequency_type: frequencyType,
      target_value: targetValue !== "" ? Number(targetValue) : undefined,
      target_unit: targetUnit || undefined,
      goal_id: goalId ? goalId : null,
    };

    try {
      setActionLoadingId("saving");
      if (editingHabit) {
        await habitsApi.updateHabit(accessToken, editingHabit.id, payload);
      } else {
        await habitsApi.createHabit(accessToken, payload);
      }
      setIsModalOpen(false);
      resetForm();
      fetchHabitsAndGoals();
    } catch (err: any) {
      setError(err?.message || "Failed to save habit.");
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleComplete = async (habitId: string) => {
    if (!accessToken) return;
    try {
      setActionLoadingId(habitId);
      const res = await habitsApi.completeHabit(accessToken, habitId);

      // Optimistically update habit list
      setHabits((prev) =>
        prev.map((h) => {
          if (h.id === habitId) {
            return {
              ...h,
              completed_today: true,
              current_streak: res.streak.current_streak,
              best_streak: res.streak.best_streak,
              total_completions: res.streak.total_completions,
            };
          }
          return h;
        })
      );
    } catch (err: any) {
      setError(err?.message || "Failed to complete habit.");
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleArchive = async (habitId: string, currentArchived: boolean) => {
    if (!accessToken) return;
    try {
      setActionLoadingId(habitId);
      await habitsApi.archiveHabit(accessToken, habitId, !currentArchived);
      fetchHabitsAndGoals();
    } catch (err: any) {
      setError(err?.message || "Failed to archive habit.");
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleDelete = async (habitId: string) => {
    if (!accessToken || !confirm("Are you sure you want to delete this habit?")) return;
    try {
      setActionLoadingId(habitId);
      await habitsApi.deleteHabit(accessToken, habitId);
      setHabits((prev) => prev.filter((h) => h.id !== habitId));
    } catch (err: any) {
      setError(err?.message || "Failed to delete habit.");
    } finally {
      setActionLoadingId(null);
    }
  };

  const activeHabitsCount = habits.filter((h) => !h.is_archived).length;
  const isFreePlan = user?.subscription_tier === "free";
  const limitReached = isFreePlan && activeHabitsCount >= 5;

  return (
    <main className="min-h-screen bg-[#0f0f0f] text-white p-6 max-w-4xl mx-auto space-y-8">
      {/* Top Header */}
      <header className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#2e2e2e] pb-6">
        <div className="space-y-1">
          <div className="flex items-center gap-3">
            <Link
              href="/dashboard"
              className="p-2 text-neutral-400 hover:text-white hover:bg-[#242424] rounded-xl border border-[#333] transition"
            >
              <ArrowLeft className="w-4 h-4" />
            </Link>
            <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight">
              Habits Manager
            </h1>
          </div>
          <p className="text-xs text-neutral-400 pl-11">
            Create, track, and maintain your high-leverage daily routines.
          </p>
        </div>

        <div className="flex items-center gap-3 self-start sm:self-auto">
          <Link
            href="/goals"
            className="flex items-center gap-1.5 px-3.5 py-2.5 bg-[#242424] hover:bg-[#2e2e2e] text-white text-xs font-semibold rounded-xl border border-[#333] transition"
          >
            <Target className="w-4 h-4 text-indigo-400" />
            <span>Goals</span>
          </Link>

          <button
            onClick={handleOpenCreateModal}
            disabled={activeTab === "active" && limitReached}
            className="flex items-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-xl shadow-lg shadow-indigo-600/20 disabled:opacity-50 transition"
          >
            <Plus className="w-4 h-4" />
            <span>New Habit</span>
          </button>
        </div>
      </header>

      {/* Free Tier Usage Banner */}
      {isFreePlan && (
        <div className="bg-[#1a1a1a] border border-[#2e2e2e] rounded-2xl p-4 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-indigo-600/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <p className="text-xs font-semibold text-white">
                Free Plan: {activeHabitsCount} / 5 Active Habits
              </p>
              <p className="text-[11px] text-neutral-400">
                Upgrade to Pro for unlimited active habits and AI insights.
              </p>
            </div>
          </div>

          <button
            onClick={() => alert("Pro subscription checkout coming soon!")}
            className="px-3 py-1.5 bg-indigo-600/10 hover:bg-indigo-600/20 border border-indigo-500/30 text-indigo-400 text-xs font-semibold rounded-xl transition flex-shrink-0"
          >
            Upgrade
          </button>
        </div>
      )}

      {/* Error Callout */}
      {error && (
        <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-xs flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
          <button onClick={() => setError(null)} className="text-red-400 hover:text-white">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Navigation Tabs */}
      <div className="flex items-center justify-between border-b border-[#2e2e2e] pb-2">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setActiveTab("active")}
            className={`px-4 py-2 text-xs font-semibold rounded-xl transition ${
              activeTab === "active"
                ? "bg-[#242424] text-white border border-[#333]"
                : "text-neutral-400 hover:text-white"
            }`}
          >
            Active Habits
          </button>
          <button
            onClick={() => setActiveTab("archived")}
            className={`px-4 py-2 text-xs font-semibold rounded-xl transition ${
              activeTab === "archived"
                ? "bg-[#242424] text-white border border-[#333]"
                : "text-neutral-400 hover:text-white"
            }`}
          >
            Archived
          </button>
        </div>
      </div>

      {/* Habit Cards List */}
      {isFetching ? (
        <div className="py-16 text-center text-xs text-neutral-400 animate-pulse">
          Loading habits...
        </div>
      ) : habits.length === 0 ? (
        <div className="text-center py-16 bg-[#1a1a1a] border border-[#2e2e2e] rounded-2xl p-8 space-y-4">
          <div className="w-12 h-12 rounded-2xl bg-[#242424] flex items-center justify-center text-neutral-400 mx-auto">
            <Target className="w-6 h-6" />
          </div>
          <div className="space-y-1">
            <h3 className="text-sm font-bold text-white">
              {activeTab === "active" ? "No active habits found" : "No archived habits"}
            </h3>
            <p className="text-xs text-neutral-400">
              {activeTab === "active"
                ? "Create your first habit to start building your streak."
                : "Archived habits will appear here."}
            </p>
          </div>
          {activeTab === "active" && (
            <button
              onClick={handleOpenCreateModal}
              className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-xl shadow-lg shadow-indigo-600/20 transition"
            >
              <Plus className="w-4 h-4" />
              <span>Create Habit</span>
            </button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-3">
          {habits.map((habit) => {
            const isLoadingAction = actionLoadingId === habit.id;
            const linkedGoal = goals.find((g) => g.id === habit.goal_id);

            return (
              <div
                key={habit.id}
                className="bg-[#1a1a1a] border border-[#2e2e2e] hover:border-[#3e3e3e] rounded-2xl p-5 shadow-lg flex flex-col md:flex-row md:items-center justify-between gap-4 transition"
              >
                <div className="space-y-2 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="px-2 py-0.5 rounded-md bg-[#242424] text-neutral-400 text-[10px] font-semibold uppercase tracking-wider">
                      {habit.category}
                    </span>
                    <span className="px-2 py-0.5 rounded-md bg-[#242424] text-neutral-400 text-[10px] font-semibold uppercase tracking-wider">
                      {habit.frequency_type.replace("_", " ")}
                    </span>

                    {linkedGoal && (
                      <span className="px-2 py-0.5 rounded-md bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 text-[10px] font-semibold flex items-center gap-1">
                        <Target className="w-3 h-3" />
                        <span>{linkedGoal.title}</span>
                      </span>
                    )}

                    {/* Streak Flame Badge */}
                    <div className="flex items-center gap-1 text-xs font-bold text-amber-400 bg-amber-400/10 px-2 py-0.5 rounded-md border border-amber-400/20">
                      <Flame className="w-3.5 h-3.5 text-amber-500 fill-amber-500" />
                      <span>{habit.current_streak} day streak</span>
                      <span className="text-[10px] text-neutral-500 font-normal">
                        (best: {habit.best_streak})
                      </span>
                    </div>
                  </div>

                  <h3 className="text-base font-bold text-white truncate">
                    {habit.title}
                  </h3>

                  {habit.description && (
                    <p className="text-xs text-neutral-400 truncate max-w-xl">
                      {habit.description}
                    </p>
                  )}

                  {habit.target_value && (
                    <p className="text-xs text-neutral-400 font-medium">
                      Target: {habit.target_value} {habit.target_unit || ""}
                    </p>
                  )}
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2 flex-shrink-0 self-end md:self-auto">
                  <div className="flex items-center gap-1 border-r border-[#2e2e2e] pr-2">
                    <Link
                      href={`/habits/${habit.id}`}
                      className="p-2 text-neutral-400 hover:text-white hover:bg-[#242424] rounded-xl border border-[#333] transition"
                      title="View Habit History & Calendar"
                    >
                      <Activity className="w-3.5 h-3.5 text-indigo-400" />
                    </Link>
                    <button
                      onClick={() => handleOpenEditModal(habit)}
                      className="p-2 text-neutral-400 hover:text-white hover:bg-[#242424] rounded-xl border border-[#333] transition"
                      title="Edit Habit"
                    >
                      <Edit2 className="w-3.5 h-3.5" />
                    </button>
                    <button
                      onClick={() => handleArchive(habit.id, habit.is_archived)}
                      className="p-2 text-neutral-400 hover:text-white hover:bg-[#242424] rounded-xl border border-[#333] transition"
                      title={habit.is_archived ? "Restore Habit" : "Archive Habit"}
                    >
                      {habit.is_archived ? (
                        <RotateCcw className="w-3.5 h-3.5" />
                      ) : (
                        <Archive className="w-3.5 h-3.5" />
                      )}
                    </button>
                    <button
                      onClick={() => handleDelete(habit.id)}
                      className="p-2 text-neutral-400 hover:text-red-400 hover:bg-red-500/10 rounded-xl border border-[#333] transition"
                      title="Delete Habit"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>

                  {/* Complete Today Action Button */}
                  {activeTab === "active" && (
                    <button
                      onClick={() => handleComplete(habit.id)}
                      disabled={habit.completed_today || isLoadingAction}
                      className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition ${
                        habit.completed_today
                          ? "bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 cursor-default"
                          : "bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-600/20 disabled:opacity-50"
                      }`}
                    >
                      <CheckCircle2 className="w-4 h-4" />
                      <span>
                        {isLoadingAction
                          ? "Saving..."
                          : habit.completed_today
                          ? "Completed Today"
                          : "Complete Today"}
                      </span>
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Create / Edit Habit Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-[#1a1a1a] border border-[#2e2e2e] rounded-2xl w-full max-w-lg p-6 space-y-6 shadow-2xl">
            <div className="flex items-center justify-between border-b border-[#2e2e2e] pb-4">
              <h2 className="text-lg font-bold text-white">
                {editingHabit ? "Edit Habit" : "Create New Habit"}
              </h2>
              <button
                onClick={() => setIsModalOpen(false)}
                className="text-neutral-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSaveHabit} className="space-y-4">
              <div className="space-y-1.5">
                <label className="block text-xs font-medium text-neutral-300">
                  Habit Title *
                </label>
                <input
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Solve 2 DSA Problems"
                  className="w-full px-4 py-2.5 bg-[#242424] border border-[#333] rounded-xl text-white text-sm focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="space-y-1.5">
                <label className="block text-xs font-medium text-neutral-300">
                  Description
                </label>
                <textarea
                  rows={2}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="e.g. Focus on binary trees and graphs"
                  className="w-full px-4 py-2.5 bg-[#242424] border border-[#333] rounded-xl text-white text-sm focus:outline-none focus:border-indigo-500"
                />
              </div>

              {/* Goal Association Dropdown */}
              <div className="space-y-1.5">
                <label className="block text-xs font-medium text-neutral-300">
                  Associated Goal (Optional)
                </label>
                <select
                  value={goalId}
                  onChange={(e) => setGoalId(e.target.value)}
                  className="w-full px-4 py-2.5 bg-[#242424] border border-[#333] rounded-xl text-white text-sm focus:outline-none focus:border-indigo-500"
                >
                  <option value="">None (Standalone Habit)</option>
                  {goals.map((g) => (
                    <option key={g.id} value={g.id}>
                      {g.title}
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="block text-xs font-medium text-neutral-300">
                    Category *
                  </label>
                  <select
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    className="w-full px-4 py-2.5 bg-[#242424] border border-[#333] rounded-xl text-white text-sm focus:outline-none focus:border-indigo-500"
                  >
                    <option value="coding">Coding</option>
                    <option value="fitness">Fitness</option>
                    <option value="study">Study</option>
                    <option value="reading">Reading</option>
                    <option value="sleep">Sleep</option>
                    <option value="productivity">Productivity</option>
                    <option value="career">Career</option>
                    <option value="personal_growth">Personal Growth</option>
                    <option value="other">Other</option>
                  </select>
                </div>

                <div className="space-y-1.5">
                  <label className="block text-xs font-medium text-neutral-300">
                    Frequency *
                  </label>
                  <select
                    value={frequencyType}
                    onChange={(e) => setFrequencyType(e.target.value)}
                    className="w-full px-4 py-2.5 bg-[#242424] border border-[#333] rounded-xl text-white text-sm focus:outline-none focus:border-indigo-500"
                  >
                    <option value="daily">Daily</option>
                    <option value="weekdays">Weekdays (Mon-Fri)</option>
                    <option value="weekends">Weekends (Sat-Sun)</option>
                    <option value="weekly">Weekly (1x per week)</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="block text-xs font-medium text-neutral-300">
                    Target Value (Optional)
                  </label>
                  <input
                    type="number"
                    value={targetValue}
                    onChange={(e) =>
                      setTargetValue(e.target.value ? Number(e.target.value) : "")
                    }
                    placeholder="e.g. 2"
                    className="w-full px-4 py-2.5 bg-[#242424] border border-[#333] rounded-xl text-white text-sm focus:outline-none focus:border-indigo-500"
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="block text-xs font-medium text-neutral-300">
                    Target Unit (Optional)
                  </label>
                  <input
                    type="text"
                    value={targetUnit}
                    onChange={(e) => setTargetUnit(e.target.value)}
                    placeholder="e.g. problems / mins"
                    className="w-full px-4 py-2.5 bg-[#242424] border border-[#333] rounded-xl text-white text-sm focus:outline-none focus:border-indigo-500"
                  />
                </div>
              </div>

              <div className="flex items-center justify-end gap-3 pt-4 border-t border-[#2e2e2e]">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 text-xs font-semibold text-neutral-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={actionLoadingId === "saving"}
                  className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-xl shadow-lg shadow-indigo-600/20 disabled:opacity-50"
                >
                  {actionLoadingId === "saving"
                    ? "Saving..."
                    : editingHabit
                    ? "Save Changes"
                    : "Create Habit"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </main>
  );
}
