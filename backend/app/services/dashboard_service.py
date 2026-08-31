from typing import List, Set
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.habit_repository import HabitRepository
from app.repositories.habit_log_repository import HabitLogRepository
from app.services.streak_service import StreakService
from app.services.goal_service import GoalService
from app.utils.datetime_utils import get_user_today
from app.schemas.habit import HabitPublic
from app.schemas.dashboard import (
    DashboardResponse,
    DashboardUserSummary,
    TodayProgress,
    ConsistencySummary,
)


class DashboardService:
    @classmethod
    def get_dashboard_data(cls, db: Session, user: User) -> DashboardResponse:
        today = get_user_today(user.timezone)

        # Fetch all active non-archived user habits
        active_habits = HabitRepository.get_user_habits(
            db, user_id=user.id, is_active=True, is_archived=False
        )

        today_due_habits: List[HabitPublic] = []
        completed_count = 0
        total_completions_all_time = 0
        best_streak_overall = 0

        for habit in active_habits:
            completed_dates = HabitLogRepository.get_completed_dates_set(db, habit.id)
            stats = StreakService.calculate_streak_stats(habit, completed_dates, today)

            # Sync cached streak numbers on habit if updated
            if (
                habit.current_streak != stats.current_streak
                or habit.best_streak != stats.best_streak
            ):
                HabitRepository.update_cached_streak(
                    db, habit, stats.current_streak, stats.best_streak, stats.total_completions
                )

            total_completions_all_time += stats.total_completions
            if stats.best_streak > best_streak_overall:
                best_streak_overall = stats.best_streak

            # Check if habit is due today
            if StreakService.is_due_on_date(habit, today):
                habit_obj = HabitPublic.model_validate(habit)
                is_completed = today in completed_dates
                habit_obj.completed_today = is_completed

                if is_completed:
                    completed_count += 1

                today_due_habits.append(habit_obj)

        total_expected = len(today_due_habits)
        completion_pct = 0.0
        if total_expected > 0:
            completion_pct = round(min(100.0, (completed_count / total_expected) * 100.0), 1)

        # Fetch active goals with their calculated progress
        user_goals = GoalService.get_user_goals(db, user, status="active")

        return DashboardResponse(
            user=DashboardUserSummary(
                full_name=user.full_name,
                current_date=today,
                timezone=user.timezone,
            ),
            today=TodayProgress(
                total_expected_habits=total_expected,
                completed_habits=completed_count,
                completion_percentage=completion_pct,
                habits=today_due_habits,
            ),
            consistency_summary=ConsistencySummary(
                total_active_habits=len(active_habits),
                total_completions_all_time=total_completions_all_time,
                best_streak_overall=best_streak_overall,
            ),
            goals=user_goals,
        )
