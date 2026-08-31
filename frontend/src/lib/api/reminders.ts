import { apiClient } from "./client";
import {
  Reminder,
  NextReminder,
  CreateReminderPayload,
  UpdateReminderPayload,
} from "@/types";

export const remindersApi = {
  getReminders: (token: string, isActive?: boolean): Promise<Reminder[]> => {
    const params = new URLSearchParams();
    if (isActive !== undefined) params.set("is_active", String(isActive));
    const query = params.toString() ? `?${params.toString()}` : "";

    return apiClient<Reminder[]>(`/reminders${query}`, {
      method: "GET",
      token,
    });
  },

  getReminder: (token: string, id: string): Promise<Reminder> => {
    return apiClient<Reminder>(`/reminders/${id}`, {
      method: "GET",
      token,
    });
  },

  getNextReminder: (token: string): Promise<NextReminder | null> => {
    return apiClient<NextReminder | null>("/reminders/next", {
      method: "GET",
      token,
    });
  },

  createReminder: (
    token: string,
    payload: CreateReminderPayload
  ): Promise<Reminder> => {
    return apiClient<Reminder>("/reminders", {
      method: "POST",
      token,
      body: JSON.stringify(payload),
    });
  },

  updateReminder: (
    token: string,
    id: string,
    payload: UpdateReminderPayload
  ): Promise<Reminder> => {
    return apiClient<Reminder>(`/reminders/${id}`, {
      method: "PATCH",
      token,
      body: JSON.stringify(payload),
    });
  },

  deleteReminder: (token: string, id: string): Promise<void> => {
    return apiClient<void>(`/reminders/${id}`, {
      method: "DELETE",
      token,
    });
  },
};
