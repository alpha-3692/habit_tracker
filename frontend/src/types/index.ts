export type Category =
  | "fitness"
  | "study"
  | "coding"
  | "reading"
  | "sleep"
  | "productivity"
  | "career"
  | "personal_growth"
  | "other";

export type FrequencyType = "daily" | "specific_days" | "weekdays" | "weekends" | "weekly";

export type SubscriptionTier = "free" | "pro";

export interface User {
  id: string;
  email: string;
  username: string | null;
  full_name: string | null;
  avatar_url: string | null;
  timezone: string;
  subscription_tier: SubscriptionTier;
  onboarding_completed: boolean;
  created_at: string;
}

export interface GoalHabitSummary {
  id: string;
  title: string;
  category: Category;
  current_streak: number;
  completion_percentage: number;
}

export interface Goal {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  category: Category;
  status: "active" | "completed" | "archived";
  target_date: string | null;
  habit_count: number;
  progress_percentage: number;
  habits?: GoalHabitSummary[];
  created_at: string;
  updated_at: string;
}

export interface Habit {
  id: string;
  user_id: string;
  goal_id: string | null;
  title: string;
  description: string | null;
  category: Category;
  frequency_type: FrequencyType;
  frequency_days: number[] | null;
  target_value: number | null;
  target_unit: string | null;
  color: string | null;
  icon: string | null;
  start_date: string;
  end_date: string | null;
  is_active: boolean;
  is_archived: boolean;
  current_streak: number;
  best_streak: number;
  total_completions: number;
  order_index: number;
  completed_today?: boolean;
  created_at: string;
  updated_at: string;
}

export interface HabitLog {
  id: string;
  habit_id: string;
  user_id: string;
  completed_date: string;
  completed_at: string;
  value: number | null;
  notes: string | null;
  created_at: string;
}

export interface DashboardData {
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

export interface DayHistory {
  date: string;
  is_due: boolean;
  is_completed: boolean;
  value: number | null;
  notes: string | null;
  completed_at: string | null;
}

export interface HabitHistoryResponse {
  habit: Habit;
  start_date: string;
  end_date: string;
  days: DayHistory[];
}

export interface CalendarDaySummary {
  date: string;
  expected: number;
  completed: number;
  percentage: number;
}

export interface CalendarResponse {
  start_date: string;
  end_date: string;
  days: CalendarDaySummary[];
}

export interface WeeklyTrendItem {
  week_start: string;
  week_end: string;
  expected: number;
  completed: number;
  percentage: number;
}

export interface DayOfWeekItem {
  day_name: string;
  day_index: number;
  expected: number;
  completed: number;
  percentage: number;
}

export interface CategoryPerformanceItem {
  category: Category;
  habit_count: number;
  expected: number;
  completed: number;
  percentage: number;
}

export interface BehaviorInsight {
  type: string;
  title: string;
  description: string;
  impact: "positive" | "neutral" | "warning";
}

export interface AnalyticsTrendsResponse {
  time_range_days: number;
  overall_consistency: number;
  total_habits_tracked: number;
  total_completions: number;
  momentum_score: number;
  weekly_trends: WeeklyTrendItem[];
  day_of_week: DayOfWeekItem[];
  category_breakdown: CategoryPerformanceItem[];
  insights: BehaviorInsight[];
}

export interface Achievement {
  id: string;
  code: string;
  title: string;
  description: string;
  icon: string | null;
  category: string;
  criteria_type: string;
  criteria_value: number;
  is_active: boolean;
}

export interface UserAchievement {
  id: string;
  user_id: string;
  achievement_id: string;
  habit_id: string | null;
  unlocked_at: string;
  achievement?: Achievement;
}

export interface AchievementWithProgress {
  id: string;
  code: string;
  title: string;
  description: string;
  icon: string | null;
  category: string;
  criteria_type: string;
  criteria_value: number;
  is_unlocked: boolean;
  unlocked_at: string | null;
  progress: number;
  target: number;
  progress_percentage: number;
}

export interface Reminder {
  id: string;
  habit_id: string;
  habit_title: string | null;
  habit_category: Category | null;
  user_id: string;
  reminder_time: string; // "HH:MM:SS" or "HH:MM"
  days_of_week: number[] | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface NextReminder {
  reminder_id: string;
  habit_id: string;
  habit_title: string;
  habit_category: Category;
  reminder_time: string;
  next_occurrence: string;
}

export interface CreateReminderPayload {
  habit_id: string;
  reminder_time: string;
  days_of_week?: number[] | null;
  is_active?: boolean;
}

export interface UpdateReminderPayload {
  reminder_time?: string;
  days_of_week?: number[] | null;
  is_active?: boolean;
}
