import { apiClient } from "./client";
import { CalendarResponse, AnalyticsTrendsResponse } from "@/types";

export const analyticsApi = {
  getCalendarSummary: (
    token: string,
    startDate?: string,
    endDate?: string,
    habitId?: string
  ): Promise<CalendarResponse> => {
    const params = new URLSearchParams();
    if (startDate) params.set("start_date", startDate);
    if (endDate) params.set("end_date", endDate);
    if (habitId) params.set("habit_id", habitId);
    const query = params.toString() ? `?${params.toString()}` : "";

    return apiClient<CalendarResponse>(`/analytics/calendar${query}`, {
      method: "GET",
      token,
    });
  },

  getAnalyticsTrends: (
    token: string,
    days: number = 30
  ): Promise<AnalyticsTrendsResponse> => {
    return apiClient<AnalyticsTrendsResponse>(`/analytics/trends?days=${days}`, {
      method: "GET",
      token,
    });
  },
};
