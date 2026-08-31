import { apiClient } from "./client";
import { User } from "@/types";

export interface RegisterPayload {
  email: string;
  password: string;
  full_name?: string;
  timezone?: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface AuthResponseData {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export const authApi = {
  register: (payload: RegisterPayload): Promise<AuthResponseData> => {
    return apiClient<AuthResponseData>("/auth/register", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  login: (payload: LoginPayload): Promise<AuthResponseData> => {
    return apiClient<AuthResponseData>("/auth/login", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  refresh: (refreshToken: string): Promise<{ access_token: string; token_type: string }> => {
    return apiClient("/auth/refresh", {
      method: "POST",
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
  },

  getMe: (accessToken: string): Promise<User> => {
    return apiClient<User>("/users/me", {
      method: "GET",
      token: accessToken,
    });
  },
};
