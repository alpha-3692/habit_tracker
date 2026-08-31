import { apiClient } from "./client";
import { HabitHistoryResponse } from "@/types";

export const historyApi = {
  getHabitHistory: (
    token: string,
    habitId: string,
    startDate?: string,
    endDate?: string
  ): Promise<HabitHistoryResponse> => {
    const params = new URLSearchParams();
    if (startDate) params.set("start_date", startDate);
    if (endDate) params.set("end_date", endDate);
    const query = params.toString() ? `?${params.toString()}` : "";

    return apiClient<HabitHistoryResponse>(`/habits/${habitId}/history${query}`, {
      method: "GET",
      token,
    });
  },
};
