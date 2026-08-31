import { apiClient } from "./client";
import { Habit } from "@/types";

export interface CreateHabitPayload {
  title: string;
  description?: string;
  category: string;
  goal_id?: string | null;
  frequency_type?: string;
  frequency_days?: number[];
  target_value?: number;
  target_unit?: string;
  color?: string;
  icon?: string;
  start_date?: string;
}

export interface CompleteHabitResponse {
  log_id: string;
  habit_id: string;
  completed_date: string;
  streak: {
    current_streak: number;
    best_streak: number;
    total_completions: number;
  };
  achievements_unlocked: string[];
}

export const habitsApi = {
  getHabits: (
    token: string,
    params?: { is_active?: boolean; is_archived?: boolean; goal_id?: string }
  ): Promise<Habit[]> => {
    const query = new URLSearchParams();
    if (params?.is_active !== undefined) query.set("is_active", String(params.is_active));
    if (params?.is_archived !== undefined) query.set("is_archived", String(params.is_archived));
    if (params?.goal_id) query.set("goal_id", params.goal_id);

    const queryString = query.toString() ? `?${query.toString()}` : "";
    return apiClient<Habit[]>(`/habits${queryString}`, {
      method: "GET",
      token,
    });
  },

  createHabit: (token: string, payload: CreateHabitPayload): Promise<Habit> => {
    return apiClient<Habit>("/habits", {
      method: "POST",
      token,
      body: JSON.stringify(payload),
    });
  },

  updateHabit: (
    token: string,
    habitId: string,
    payload: Partial<CreateHabitPayload>
  ): Promise<Habit> => {
    return apiClient<Habit>(`/habits/${habitId}`, {
      method: "PATCH",
      token,
      body: JSON.stringify(payload),
    });
  },

  archiveHabit: (token: string, habitId: string, isArchived: boolean): Promise<Habit> => {
    return apiClient<Habit>(`/habits/${habitId}/archive?is_archived=${isArchived}`, {
      method: "PATCH",
      token,
    });
  },

  deleteHabit: (token: string, habitId: string): Promise<void> => {
    return apiClient<void>(`/habits/${habitId}`, {
      method: "DELETE",
      token,
    });
  },

  completeHabit: (
    token: string,
    habitId: string,
    payload?: { value?: number; notes?: string; completed_date?: string }
  ): Promise<CompleteHabitResponse> => {
    return apiClient<CompleteHabitResponse>(`/habits/${habitId}/complete`, {
      method: "POST",
      token,
      body: JSON.stringify(payload || {}),
    });
  },
};
