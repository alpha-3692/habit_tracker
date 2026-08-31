from datetime import date, timedelta
from typing import Set, Tuple, List, Optional
from app.models.habit import Habit


class StreakStats:
    def __init__(
        self,
        current_streak: int,
        best_streak: int,
        total_completions: int,
        completion_percentage: float,
    ):
        self.current_streak = current_streak
        self.best_streak = best_streak
        self.total_completions = total_completions
        self.completion_percentage = completion_percentage


class StreakService:
    @staticmethod
    def is_due_on_date(habit: Habit, check_date: date) -> bool:
        """
        Determines whether a habit was scheduled/due on a specific date.
        Must be on or after start_date, and on or before end_date (if set).
        """
        if check_date < habit.start_date:
            return False
        if habit.end_date and check_date > habit.end_date:
            return False

        freq_type = habit.frequency_type
        weekday = check_date.weekday()  # 0=Mon, 6=Sun

        if freq_type == "daily":
            return True
        elif freq_type == "weekdays":
            return weekday in (0, 1, 2, 3, 4)
        elif freq_type == "weekends":
            return weekday in (5, 6)
        elif freq_type == "specific_days":
            if not habit.frequency_days:
                return True
            return weekday in habit.frequency_days
        elif freq_type == "weekly":
            # For weekly habits, every day can be a completion day,
            # but frequency evaluation operates on calendar weeks.
            return True

        return True

    @classmethod
    def calculate_streak_stats(
        cls,
        habit: Habit,
        completed_dates: Set[date],
        today: date,
    ) -> StreakStats:
        """
        Authoritative calculation of current streak, best streak, total completions,
        and completion percentage derived entirely from completed_dates set.
        """
        total_completions = len(completed_dates)

        if habit.frequency_type == "weekly":
            return cls._calculate_weekly_streak_stats(habit, completed_dates, today)

        # ── Daily / Specific Days / Weekdays / Weekends calculation ────────────

        # Calculate current streak: walk backwards from today
        current_streak = 0
        curr_date = today

        # If today is due but not yet completed, we start checking from yesterday so today doesn't break streak
        if curr_date not in completed_dates and cls.is_due_on_date(habit, curr_date):
            curr_date -= timedelta(days=1)

        while curr_date >= habit.start_date:
            if cls.is_due_on_date(habit, curr_date):
                if curr_date in completed_dates:
                    current_streak += 1
                else:
                    # Due date missed -> streak broken
                    break
            curr_date -= timedelta(days=1)

        # Calculate best streak & completion percentage by walking forward from start_date
        best_streak = 0
        running_streak = 0
        total_due_days = 0

        d = habit.start_date
        end_check = min(today, habit.end_date) if habit.end_date else today

        while d <= end_check:
            if cls.is_due_on_date(habit, d):
                total_due_days += 1
                if d in completed_dates:
                    running_streak += 1
                    best_streak = max(best_streak, running_streak)
                else:
                    # If missed on a past date, reset running streak
                    if d < today:
                        running_streak = 0
            d += timedelta(days=1)

        # Ensure current_streak is included in best_streak
        best_streak = max(best_streak, current_streak)

        completion_pct = 0.0
        if total_due_days > 0:
            completion_pct = round(min(100.0, (total_completions / total_due_days) * 100.0), 1)

        return StreakStats(
            current_streak=current_streak,
            best_streak=best_streak,
            total_completions=total_completions,
            completion_percentage=completion_pct,
        )

    @classmethod
    def _calculate_weekly_streak_stats(
        cls,
        habit: Habit,
        completed_dates: Set[date],
        today: date,
    ) -> StreakStats:
        """
        Weekly frequency streak algorithm:
        Grouping completion dates by ISO calendar week (year, iso_week).
        A week is considered completed if at least one completion occurred in that week.
        """
        total_completions = len(completed_dates)
        if not completed_dates:
            return StreakStats(0, 0, 0, 0.0)

        # Map dates to (year, week)
        completed_weeks = {d.isocalendar()[:2] for d in completed_dates}

        current_year, current_week, _ = today.isocalendar()
        start_year, start_week, _ = habit.start_date.isocalendar()

        # Build list of all weeks from start_date to today
        all_weeks: List[Tuple[int, int]] = []
        d = habit.start_date
        while d <= today:
            iso_wk = d.isocalendar()[:2]
            if not all_weeks or all_weeks[-1] != iso_wk:
                all_weeks.append(iso_wk)
            d += timedelta(days=1)

        # Current streak in weeks
        current_streak = 0
        # Check current week first
        if (current_year, current_week) in completed_weeks:
            check_idx = len(all_weeks) - 1
        else:
            # Current week not yet completed — start checking from last week
            check_idx = len(all_weeks) - 2

        while check_idx >= 0:
            wk = all_weeks[check_idx]
            if wk in completed_weeks:
                current_streak += 1
                check_idx -= 1
            else:
                break

        # Best streak in weeks
        best_streak = 0
        running_streak = 0

        for idx, wk in enumerate(all_weeks):
            if wk in completed_weeks:
                running_streak += 1
                best_streak = max(best_streak, running_streak)
            else:
                # If past week was missed, reset
                if idx < len(all_weeks) - 1:
                    running_streak = 0

        best_streak = max(best_streak, current_streak)
        total_weeks = len(all_weeks)
        pct = round(min(100.0, (len(completed_weeks) / total_weeks) * 100.0), 1) if total_weeks > 0 else 0.0

        return StreakStats(
            current_streak=current_streak,
            best_streak=best_streak,
            total_completions=total_completions,
            completion_percentage=pct,
        )
