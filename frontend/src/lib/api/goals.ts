import { apiClient } from "./client";
import { Goal } from "@/types";

export interface GoalCreatePayload {
  title: string;
  description?: string;
  category: string;
  target_date?: string | null;
}

export interface GoalUpdatePayload {
  title?: string;
  description?: string;
  category?: string;
  status?: "active" | "completed" | "archived";
  target_date?: string | null;
}

export const goalsApi = {
  getGoals: (token: string, status?: string): Promise<Goal[]> => {
    const query = status ? `?status=${status}` : "";
    return apiClient<Goal[]>(`/goals${query}`, {
      method: "GET",
      token,
    });
  },

  getGoalById: (token: string, goalId: string): Promise<Goal> => {
    return apiClient<Goal>(`/goals/${goalId}`, {
      method: "GET",
      token,
    });
  },

  createGoal: (token: string, payload: GoalCreatePayload): Promise<Goal> => {
    return apiClient<Goal>("/goals", {
      method: "POST",
      body: JSON.stringify(payload),
      token,
    });
  },

  updateGoal: (
    token: string,
    goalId: string,
    payload: GoalUpdatePayload
  ): Promise<Goal> => {
    return apiClient<Goal>(`/goals/${goalId}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
      token,
    });
  },

  deleteGoal: (token: string, goalId: string): Promise<void> => {
    return apiClient<void>(`/goals/${goalId}`, {
      method: "DELETE",
      token,
    });
  },
};
