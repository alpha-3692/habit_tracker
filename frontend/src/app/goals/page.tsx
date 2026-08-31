"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/context/AuthContext";
import { goalsApi } from "@/lib/api/goals";
import { Goal, Category } from "@/types";
import { GoalCard } from "@/components/goals/GoalCard";
import { GoalModal } from "@/components/goals/GoalModal";
import { EmptyGoalsState } from "@/components/goals/EmptyGoalsState";
import {
  ArrowLeft,
  Plus,
  Target,
  Sparkles,
  Layers,
  AlertCircle,
  RefreshCw,
  X,
} from "lucide-react";

export default function GoalsPage() {
  const router = useRouter();
  const { user, accessToken, isLoading } = useAuth();

  const [goals, setGoals] = useState<Goal[]>([]);
  const [isFetching, setIsFetching] = useState(true);
  const [activeTab, setActiveTab] = useState<"active" | "completed">("active");
  const [error, setError] = useState<string | null>(null);

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingGoal, setEditingGoal] = useState<Goal | null>(null);

  const fetchGoals = async () => {
    if (!accessToken) return;
    try {
      setIsFetching(true);
      setError(null);
      const res = await goalsApi.getGoals(accessToken);
      setGoals(res);
    } catch (err: any) {
      setError(err?.message || "Failed to load goals.");
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
      fetchGoals();
    }
  }, [isLoading, user, accessToken]);

  const handleSaveGoal = async (data: {
    title: string;
    description?: string;
    category: Category;
    target_date?: string | null;
    status?: "active" | "completed" | "archived";
  }) => {
    if (!accessToken) return;
    if (editingGoal) {
      await goalsApi.updateGoal(accessToken, editingGoal.id, data);
    } else {
      await goalsApi.createGoal(accessToken, data);
    }
    fetchGoals();
  };

  const handleDeleteGoal = async (goalId: string) => {
    if (!accessToken) return;
    if (!confirm("Are you sure you want to delete this goal? Linked habits will be unlinked safely.")) {
      return;
    }
    try {
      await goalsApi.deleteGoal(accessToken, goalId);
      fetchGoals();
    } catch (err: any) {
      setError(err?.message || "Failed to delete goal.");
    }
  };

  const handleToggleStatus = async (goal: Goal) => {
    if (!accessToken) return;
    try {
      const newStatus = goal.status === "completed" ? "active" : "completed";
      await goalsApi.updateGoal(accessToken, goal.id, { status: newStatus });
      fetchGoals();
    } catch (err: any) {
      setError(err?.message || "Failed to update goal status.");
    }
  };

  const filteredGoals = goals.filter((g) =>
    activeTab === "active" ? g.status === "active" : g.status === "completed"
  );

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
              Goals
            </h1>
          </div>
          <p className="text-xs text-neutral-400 pl-11">
            Turn your long-term ambitions into consistent daily execution.
          </p>
        </div>

        <button
          onClick={() => {
            setEditingGoal(null);
            setIsModalOpen(true);
          }}
          className="flex items-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-xl shadow-lg shadow-indigo-600/20 transition self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" />
          <span>New Goal</span>
        </button>
      </header>

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

      {/* Navigation Tabs: Active vs Completed */}
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
            Active ({goals.filter((g) => g.status === "active").length})
          </button>
          <button
            onClick={() => setActiveTab("completed")}
            className={`px-4 py-2 text-xs font-semibold rounded-xl transition ${
              activeTab === "completed"
                ? "bg-[#242424] text-white border border-[#333]"
                : "text-neutral-400 hover:text-white"
            }`}
          >
            Completed ({goals.filter((g) => g.status === "completed").length})
          </button>
        </div>
      </div>

      {/* Goals Content */}
      {isFetching ? (
        <div className="py-16 text-center text-xs text-neutral-400 animate-pulse">
          Loading goals...
        </div>
      ) : filteredGoals.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredGoals.map((goal) => (
            <GoalCard
              key={goal.id}
              goal={goal}
              onEdit={(g) => {
                setEditingGoal(g);
                setIsModalOpen(true);
              }}
              onDelete={handleDeleteGoal}
              onToggleStatus={handleToggleStatus}
            />
          ))}
        </div>
      ) : (
        <EmptyGoalsState
          onCreate={() => {
            setEditingGoal(null);
            setIsModalOpen(true);
          }}
        />
      )}

      {/* Goal Modal */}
      <GoalModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleSaveGoal}
        initialData={editingGoal}
      />
    </main>
  );
}
