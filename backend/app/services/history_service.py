from datetime import date, timedelta
from typing import Optional, List, Set, Dict
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.models.habit import Habit
from app.repositories.habit_repository import HabitRepository
from app.repositories.habit_log_repository import HabitLogRepository
from app.services.streak_service import StreakService
from app.utils.datetime_utils import get_user_today
from app.core.exceptions import HabitNotFoundException, ForbiddenException
from app.schemas.habit import HabitPublic
from app.schemas.history import (
    DayHistory,
    HabitHistoryResponse,
    CalendarDaySummary,
    CalendarResponse,
)


class HistoryService:
    MAX_RANGE_DAYS = 365

    @classmethod
    def _validate_date_range(cls, start_date: date, end_date: date) -> None:
        if start_date > end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_date cannot be after end_date.",
            )
        range_days = (end_date - start_date).days + 1
        if range_days > cls.MAX_RANGE_DAYS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Date range cannot exceed {cls.MAX_RANGE_DAYS} days.",
            )

    @classmethod
    def get_habit_history(
        cls,
        db: Session,
        user: User,
        habit_id: UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> HabitHistoryResponse:
        habit = HabitRepository.get_by_id(db, habit_id)
        if not habit:
            raise HabitNotFoundException()
        if habit.user_id != user.id:
            raise ForbiddenException("You do not have permission to access this habit")

        today = get_user_today(user.timezone)

        # Default range: last 30 days if not provided
        if not end_date:
            end_date = today
        if not start_date:
            start_date = end_date - timedelta(days=29)

        cls._validate_date_range(start_date, end_date)

        # Fetch logs for habit in range
        logs = HabitLogRepository.get_logs_for_habit_range(
            db, habit.id, start_date, end_date
        )
        log_map = {log.completed_date: log for log in logs}

        # Build day-by-day history
        days: List[DayHistory] = []
        curr = start_date
        while curr <= end_date:
            is_due = StreakService.is_due_on_date(habit, curr)
            log = log_map.get(curr)
            is_completed = log is not None

            days.append(
                DayHistory(
                    date=curr,
                    is_due=is_due,
                    is_completed=is_completed,
                    value=float(log.value) if log and log.value is not None else None,
                    notes=log.notes if log else None,
                    completed_at=log.completed_at if log else None,
                )
            )
            curr += timedelta(days=1)

        # Enrich habit stats
        all_completed_dates = HabitLogRepository.get_completed_dates_set(db, habit.id)
        stats = StreakService.calculate_streak_stats(habit, all_completed_dates, today)
        habit_obj = HabitPublic.model_validate(habit)
        habit_obj.current_streak = stats.current_streak
        habit_obj.best_streak = stats.best_streak
        habit_obj.total_completions = stats.total_completions
        habit_obj.completed_today = today in all_completed_dates

        return HabitHistoryResponse(
            habit=habit_obj,
            start_date=start_date,
            end_date=end_date,
            days=days,
        )

    @classmethod
    def get_calendar_summary(
        cls,
        db: Session,
        user: User,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        habit_id: Optional[UUID] = None,
    ) -> CalendarResponse:
        today = get_user_today(user.timezone)

        # Default range: last 30 days if not provided
        if not end_date:
            end_date = today
        if not start_date:
            start_date = end_date - timedelta(days=29)

        cls._validate_date_range(start_date, end_date)

        # Fetch relevant habits
        if habit_id:
            habit = HabitRepository.get_by_id(db, habit_id)
            if not habit:
                raise HabitNotFoundException()
            if habit.user_id != user.id:
                raise ForbiddenException("You do not have permission to access this habit")
            habits = [habit] if (habit.is_active and not habit.is_archived and not habit.is_deleted) else []
        else:
            habits = HabitRepository.get_user_habits(
                db, user_id=user.id, is_active=True, is_archived=False
            )

        # Fetch logs for range
        logs = HabitLogRepository.get_logs_for_user_range(
            db, user_id=user.id, start_date=start_date, end_date=end_date, habit_id=habit_id
        )
        completed_pairs: Set[tuple] = {(log.habit_id, log.completed_date) for log in logs}

        days_summary: List[CalendarDaySummary] = []
        curr = start_date
        while curr <= end_date:
            due_habits = [h for h in habits if StreakService.is_due_on_date(h, curr)]
            expected_count = len(due_habits)
            completed_count = sum(
                1 for h in due_habits if (h.id, curr) in completed_pairs
            )

            pct = 0.0
            if expected_count > 0:
                pct = round(min(100.0, (completed_count / expected_count) * 100.0), 1)

            days_summary.append(
                CalendarDaySummary(
                    date=curr,
                    expected=expected_count,
                    completed=completed_count,
                    percentage=pct,
                )
            )
            curr += timedelta(days=1)

        return CalendarResponse(
            start_date=start_date,
            end_date=end_date,
            days=days_summary,
        )
