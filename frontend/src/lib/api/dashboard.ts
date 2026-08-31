import { apiClient } from "./client";
import { Habit, Goal } from "@/types";

export interface DashboardResponseData {
  user: {
    full_name: string | null;
    current_date: string;
    timezone: string;
  };
  today: {
    total_expected_habits: number;
    completed_habits: number;
    completion_percentage: number;
    habits: Habit[];
  };
  consistency_summary: {
    total_active_habits: number;
    total_completions_all_time: number;
    best_streak_overall: number;
  };
  goals?: Goal[];
}

export const dashboardApi = {
  getDashboard: (token: string): Promise<DashboardResponseData> => {
    return apiClient<DashboardResponseData>("/dashboard", {
      method: "GET",
      token,
    });
  },
};
