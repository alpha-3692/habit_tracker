import { apiClient } from "./client";
import { Achievement, AchievementWithProgress } from "@/types";

export const achievementsApi = {
  getAchievements: (token: string): Promise<Achievement[]> => {
    return apiClient<Achievement[]>("/achievements", {
      method: "GET",
      token,
    });
  },

  getMyAchievements: (token: string): Promise<AchievementWithProgress[]> => {
    return apiClient<AchievementWithProgress[]>("/achievements/me", {
      method: "GET",
      token,
    });
  },
};
