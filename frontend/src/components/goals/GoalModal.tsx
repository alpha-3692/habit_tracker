"use client";

import { useState, useEffect } from "react";
import { Goal, Category } from "@/types";
import { X, Target } from "lucide-react";

interface GoalModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: {
    title: string;
    description?: string;
    category: Category;
    target_date?: string | null;
    status?: "active" | "completed" | "archived";
  }) => Promise<void>;
  initialData?: Goal | null;
}

const CATEGORIES: Category[] = [
  "fitness",
  "study",
  "coding",
  "reading",
  "sleep",
  "productivity",
  "career",
  "personal_growth",
  "other",
];

export function GoalModal({
  isOpen,
  onClose,
  onSubmit,
  initialData,
}: GoalModalProps) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState<Category>("coding");
  const [targetDate, setTargetDate] = useState("");
  const [status, setStatus] = useState<"active" | "completed" | "archived">("active");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (initialData) {
      setTitle(initialData.title);
      setDescription(initialData.description || "");
      setCategory(initialData.category);
      setTargetDate(initialData.target_date || "");
      setStatus(initialData.status);
    } else {
      setTitle("");
      setDescription("");
      setCategory("coding");
      setTargetDate("");
      setStatus("active");
    }
    setError(null);
  }, [initialData, isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) {
      setError("Title is required.");
      return;
    }

    try {
      setIsSubmitting(true);
      setError(null);
      await onSubmit({
        title: title.trim(),
        description: description.trim() || undefined,
        category,
        target_date: targetDate ? targetDate : null,
        status,
      });
      onClose();
    } catch (err: any) {
      setError(err?.message || "Failed to save goal.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
      <div className="bg-[#1a1a1a] border border-[#2e2e2e] rounded-2xl w-full max-w-lg overflow-hidden shadow-2xl space-y-6 p-6">
        <div className="flex items-center justify-between border-b border-[#2e2e2e] pb-4">
          <div className="flex items-center gap-2">
            <Target className="w-5 h-5 text-indigo-400" />
            <h2 className="text-lg font-bold text-white tracking-tight">
              {initialData ? "Edit Goal" : "Create New Goal"}
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-neutral-400 hover:text-white hover:bg-[#242424] rounded-lg transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {error && (
          <div className="p-3 bg-red-500/10 border border-red-500/20 text-red-400 text-xs rounded-xl">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-neutral-300">Goal Title *</label>
            <input
              type="text"
              required
              placeholder="e.g. Master Full-Stack Engineering"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full bg-[#121212] border border-[#333] focus:border-indigo-500 rounded-xl px-4 py-2.5 text-xs text-white outline-none transition"
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-neutral-300">Description</label>
            <textarea
              rows={2}
              placeholder="Why this outcome matters to you..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full bg-[#121212] border border-[#333] focus:border-indigo-500 rounded-xl px-4 py-2.5 text-xs text-white outline-none transition resize-none"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-neutral-300">Category</label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value as Category)}
                className="w-full bg-[#121212] border border-[#333] focus:border-indigo-500 rounded-xl px-3 py-2.5 text-xs text-white outline-none transition"
              >
                {CATEGORIES.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat.replace("_", " ")}
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-neutral-300">Target Date</label>
              <input
                type="date"
                value={targetDate}
                onChange={(e) => setTargetDate(e.target.value)}
                className="w-full bg-[#121212] border border-[#333] focus:border-indigo-500 rounded-xl px-3 py-2.5 text-xs text-white outline-none transition"
              />
            </div>
          </div>

          {initialData && (
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-neutral-300">Status</label>
              <select
                value={status}
                onChange={(e) => setStatus(e.target.value as any)}
                className="w-full bg-[#121212] border border-[#333] focus:border-indigo-500 rounded-xl px-3 py-2.5 text-xs text-white outline-none transition"
              >
                <option value="active">Active</option>
                <option value="completed">Completed</option>
                <option value="archived">Archived</option>
              </select>
            </div>
          )}

          <div className="flex items-center justify-end gap-3 pt-4 border-t border-[#2e2e2e]">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-xs font-semibold text-neutral-400 hover:text-white transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-xl shadow-lg shadow-indigo-600/20 disabled:opacity-50 transition"
            >
              {isSubmitting ? "Saving..." : initialData ? "Save Changes" : "Create Goal"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
