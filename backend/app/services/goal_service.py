from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.goal import Goal
from app.repositories.goal_repository import GoalRepository
from app.repositories.habit_log_repository import HabitLogRepository
from app.services.streak_service import StreakService
from app.utils.datetime_utils import get_user_today
from app.core.exceptions import (
    GoalNotFoundException,
    ForbiddenException,
)
from app.schemas.goal import GoalCreate, GoalUpdate, GoalPublic, GoalHabitSummary


class GoalService:
    @classmethod
    def _enrich_goal(cls, db: Session, goal: Goal, user: User) -> GoalPublic:
        """Calculates progress percentage and associated habit summaries for a goal."""
        today = get_user_today(user.timezone)

        # Filter active non-archived non-deleted associated habits
        active_habits = [
            h for h in goal.habits if h.is_active and not h.is_archived and not h.is_deleted
        ]

        habit_summaries: List[GoalHabitSummary] = []
        progress_sum = 0.0

        for h in active_habits:
            completed_dates = HabitLogRepository.get_completed_dates_set(db, h.id)
            stats = StreakService.calculate_streak_stats(h, completed_dates, today)
            progress_sum += stats.completion_percentage

            habit_summaries.append(
                GoalHabitSummary(
                    id=h.id,
                    title=h.title,
                    category=h.category,
                    current_streak=stats.current_streak,
                    completion_percentage=stats.completion_percentage,
                )
            )

        if goal.status == "completed":
            progress_percentage = 100.0
        elif len(active_habits) == 0:
            progress_percentage = 0.0
        else:
            progress_percentage = round(min(100.0, progress_sum / len(active_habits)), 1)

        return GoalPublic(
            id=goal.id,
            user_id=goal.user_id,
            title=goal.title,
            description=goal.description,
            category=goal.category,
            status=goal.status,
            target_date=goal.target_date,
            habit_count=len(active_habits),
            progress_percentage=progress_percentage,
            habits=habit_summaries,
            created_at=goal.created_at,
            updated_at=goal.updated_at,
        )

    @classmethod
    def get_user_goals(
        cls, db: Session, user: User, status: Optional[str] = None
    ) -> List[GoalPublic]:
        goals = GoalRepository.get_user_goals(db, user_id=user.id, status=status)
        return [cls._enrich_goal(db, g, user) for g in goals]

    @classmethod
    def get_goal_by_id(cls, db: Session, user: User, goal_id: UUID) -> GoalPublic:
        goal = GoalRepository.get_by_id(db, goal_id)
        if not goal:
            raise GoalNotFoundException()
        if goal.user_id != user.id:
            raise ForbiddenException("You do not have permission to access this goal")

        return cls._enrich_goal(db, goal, user)

    @classmethod
    def create_goal(cls, db: Session, user: User, payload: GoalCreate) -> GoalPublic:
        goal_data = payload.model_dump(exclude_none=True)
        goal = GoalRepository.create(db, user_id=user.id, goal_data=goal_data)
        return cls._enrich_goal(db, goal, user)

    @classmethod
    def update_goal(
        cls, db: Session, user: User, goal_id: UUID, payload: GoalUpdate
    ) -> GoalPublic:
        goal = GoalRepository.get_by_id(db, goal_id)
        if not goal:
            raise GoalNotFoundException()
        if goal.user_id != user.id:
            raise ForbiddenException("You do not have permission to access this goal")

        update_data = payload.model_dump(exclude_unset=True)
        updated_goal = GoalRepository.update(db, goal, update_data)
        return cls._enrich_goal(db, updated_goal, user)

    @classmethod
    def delete_goal(cls, db: Session, user: User, goal_id: UUID):
        goal = GoalRepository.get_by_id(db, goal_id)
        if not goal:
            raise GoalNotFoundException()
        if goal.user_id != user.id:
            raise ForbiddenException("You do not have permission to access this goal")

        GoalRepository.soft_delete(db, goal)
