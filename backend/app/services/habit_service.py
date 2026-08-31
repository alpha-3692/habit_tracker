from typing import List, Optional
from uuid import UUID
from datetime import date
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.habit import Habit
from app.repositories.habit_repository import HabitRepository
from app.repositories.habit_log_repository import HabitLogRepository
from app.services.streak_service import StreakService
from app.utils.datetime_utils import get_user_today, is_future_date
from app.core.exceptions import (
    HabitNotFoundException,
    ForbiddenException,
    BadRequestException,
    HabitLimitExceededException,
    HabitAlreadyCompletedException,
)
from app.schemas.habit import (
    HabitCreate,
    HabitUpdate,
    HabitPublic,
    HabitCompleteRequest,
    HabitCompleteResponse,
    StreakInfo,
)


class HabitService:
    @staticmethod
    def get_user_habits(
        db: Session,
        user: User,
        is_active: Optional[bool] = None,
        is_archived: Optional[bool] = None,
        goal_id: Optional[UUID] = None,
    ) -> List[HabitPublic]:
        habits = HabitRepository.get_user_habits(
            db,
            user_id=user.id,
            is_active=is_active,
            is_archived=is_archived,
            goal_id=goal_id,
        )
        today = get_user_today(user.timezone)

        result: List[HabitPublic] = []
        for habit in habits:
            # Dynamically attach completed_today status and recalculated streaks
            completed_dates = HabitLogRepository.get_completed_dates_set(db, habit.id)
            stats = StreakService.calculate_streak_stats(habit, completed_dates, today)
            
            # Sync cache if needed
            if habit.current_streak != stats.current_streak or habit.best_streak != stats.best_streak:
                HabitRepository.update_cached_streak(
                    db, habit, stats.current_streak, stats.best_streak, stats.total_completions
                )

            habit_obj = HabitPublic.model_validate(habit)
            habit_obj.completed_today = today in completed_dates
            result.append(habit_obj)

        return result

    @staticmethod
    def get_habit_by_id(db: Session, user: User, habit_id: UUID) -> HabitPublic:
        habit = HabitRepository.get_by_id(db, habit_id)
        if not habit:
            raise HabitNotFoundException()
        if habit.user_id != user.id:
            raise ForbiddenException("You do not have permission to access this habit")

        today = get_user_today(user.timezone)
        completed_dates = HabitLogRepository.get_completed_dates_set(db, habit.id)
        stats = StreakService.calculate_streak_stats(habit, completed_dates, today)

        habit_obj = HabitPublic.model_validate(habit)
        habit_obj.completed_today = today in completed_dates
        return habit_obj

    @staticmethod
    def create_habit(db: Session, user: User, payload: HabitCreate) -> HabitPublic:
        # Check Free plan limit
        if user.subscription_tier == "free":
            active_count = HabitRepository.count_active_habits(db, user.id)
            if active_count >= 5:
                raise HabitLimitExceededException(limit=5)

        habit_data = payload.model_dump(exclude_none=True)

        # Validate goal ownership if goal_id is provided
        if "goal_id" in habit_data and habit_data["goal_id"]:
            from app.repositories.goal_repository import GoalRepository
            goal = GoalRepository.get_by_id(db, habit_data["goal_id"])
            if not goal or goal.user_id != user.id:
                raise ForbiddenException("Cannot link habit to a goal you do not own")

        # Default start_date if not provided
        if "start_date" not in habit_data or not habit_data["start_date"]:
            habit_data["start_date"] = get_user_today(user.timezone)

        habit = HabitRepository.create(db, user_id=user.id, habit_data=habit_data)
        return HabitPublic.model_validate(habit)

    @staticmethod
    def update_habit(
        db: Session, user: User, habit_id: UUID, payload: HabitUpdate
    ) -> HabitPublic:
        habit = HabitRepository.get_by_id(db, habit_id)
        if not habit:
            raise HabitNotFoundException()
        if habit.user_id != user.id:
            raise ForbiddenException("You do not have permission to access this habit")

        update_data = payload.model_dump(exclude_unset=True)

        # Validate goal ownership if goal_id is being updated
        if "goal_id" in update_data and update_data["goal_id"] is not None:
            from app.repositories.goal_repository import GoalRepository
            goal = GoalRepository.get_by_id(db, update_data["goal_id"])
            if not goal or goal.user_id != user.id:
                raise ForbiddenException("Cannot link habit to a goal you do not own")

        # Check plan limit if reactivating or unarchiving
        activating = update_data.get("is_active") is True or update_data.get("is_archived") is False
        if user.subscription_tier == "free" and activating and (not habit.is_active or habit.is_archived):
            active_count = HabitRepository.count_active_habits(db, user.id)
            if active_count >= 5:
                raise HabitLimitExceededException(limit=5)

        updated_habit = HabitRepository.update(db, habit, update_data)
        return HabitPublic.model_validate(updated_habit)

    @staticmethod
    def archive_habit(
        db: Session, user: User, habit_id: UUID, is_archived: bool = True
    ) -> HabitPublic:
        habit = HabitRepository.get_by_id(db, habit_id)
        if not habit:
            raise HabitNotFoundException()
        if habit.user_id != user.id:
            raise ForbiddenException("You do not have permission to access this habit")

        # Unarchiving check
        if not is_archived and user.subscription_tier == "free":
            active_count = HabitRepository.count_active_habits(db, user.id)
            if active_count >= 5:
                raise HabitLimitExceededException(limit=5)

        archived_habit = HabitRepository.archive(db, habit, is_archived)
        return HabitPublic.model_validate(archived_habit)

    @staticmethod
    def delete_habit(db: Session, user: User, habit_id: UUID):
        habit = HabitRepository.get_by_id(db, habit_id)
        if not habit:
            raise HabitNotFoundException()
        if habit.user_id != user.id:
            raise ForbiddenException("You do not have permission to access this habit")

        HabitRepository.soft_delete(db, habit)

    @staticmethod
    def complete_habit(
        db: Session, user: User, habit_id: UUID, payload: HabitCompleteRequest
    ) -> HabitCompleteResponse:
        habit = HabitRepository.get_by_id(db, habit_id)
        if not habit:
            raise HabitNotFoundException()
        if habit.user_id != user.id:
            raise ForbiddenException("You do not have permission to access this habit")

        if not habit.is_active or habit.is_archived:
            raise BadRequestException("Cannot complete an inactive or archived habit")

        user_today = get_user_today(user.timezone)
        target_date = payload.completed_date if payload.completed_date else user_today

        if is_future_date(target_date, user.timezone):
            raise BadRequestException("Cannot complete habit for a future date")

        # Check duplicate
        existing_log = HabitLogRepository.get_log_by_habit_and_date(db, habit.id, target_date)
        if existing_log:
            raise HabitAlreadyCompletedException()

        # Create log
        log = HabitLogRepository.create_log(
            db=db,
            habit_id=habit.id,
            user_id=user.id,
            completed_date=target_date,
            value=payload.value,
            notes=payload.notes,
        )

        # Recalculate streak stats
        completed_dates = HabitLogRepository.get_completed_dates_set(db, habit.id)
        stats = StreakService.calculate_streak_stats(habit, completed_dates, user_today)

        # Update habit cache
        HabitRepository.update_cached_streak(
            db, habit, stats.current_streak, stats.best_streak, stats.total_completions
        )

        # Evaluate achievements
        from app.services.achievement_service import AchievementService
        new_achievements = AchievementService.evaluate_after_habit_completion(
            db, user_id=user.id, habit_id=habit.id
        )

        return HabitCompleteResponse(
            log_id=log.id,
            habit_id=habit.id,
            completed_date=target_date,
            streak=StreakInfo(
                current_streak=stats.current_streak,
                best_streak=stats.best_streak,
                total_completions=stats.total_completions,
            ),
            achievements_unlocked=[a.code for a in new_achievements],
        )
