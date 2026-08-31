import uuid
from typing import List, Dict, Set, Optional
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.habit import Habit
from app.models.habit_log import HabitLog
from app.models.goal import Goal
from app.models.achievement import Achievement, UserAchievement
from app.repositories.achievement_repository import AchievementRepository
from app.repositories.habit_repository import HabitRepository
from app.repositories.habit_log_repository import HabitLogRepository
from app.repositories.goal_repository import GoalRepository
from app.schemas.achievement import (
    AchievementPublic,
    UserAchievementPublic,
    AchievementWithProgress,
)


class AchievementService:
    @classmethod
    def get_all_achievements(cls, db: Session) -> List[AchievementPublic]:
        """Ensure catalog is seeded and return all achievements."""
        AchievementRepository.ensure_seeded(db)
        achievements = AchievementRepository.get_all(db, is_active=True)
        return [AchievementPublic.model_validate(a) for a in achievements]

    @classmethod
    def get_user_achievements(
        cls, db: Session, user: User
    ) -> List[AchievementWithProgress]:
        """Returns catalog with user's unlock status and deterministic progress values."""
        AchievementRepository.ensure_seeded(db)
        achievements = AchievementRepository.get_all(db, is_active=True)

        user_unlocks = AchievementRepository.get_user_unlocked_achievements(db, user.id)
        unlock_map: Dict[uuid.UUID, UserAchievement] = {
            u.achievement_id: u for u in user_unlocks
        }

        # Calculate current user metrics for progress calculations
        habits = HabitRepository.get_user_habits(db, user.id, is_active=True, is_archived=False)
        all_user_habits = HabitRepository.get_user_habits(db, user.id)
        max_streak = max([h.current_streak for h in all_user_habits], default=0)
        best_streak = max([h.best_streak for h in all_user_habits], default=0)
        max_streak_overall = max(max_streak, best_streak)

        total_completions = (
            db.query(HabitLog).filter(HabitLog.user_id == user.id).count()
        )
        active_habits_count = len(habits)

        goals_created = db.query(Goal).filter(Goal.user_id == user.id, Goal.is_deleted == False).count()
        goals_completed = db.query(Goal).filter(Goal.user_id == user.id, Goal.status == "completed", Goal.is_deleted == False).count()

        results: List[AchievementWithProgress] = []
        for ach in achievements:
            unlocked_record = unlock_map.get(ach.id)
            is_unlocked = unlocked_record is not None

            # Calculate deterministic progress
            progress = 0
            target = ach.criteria_value

            if ach.criteria_type == "streak":
                progress = max_streak_overall
            elif ach.criteria_type == "completions":
                progress = total_completions
            elif ach.criteria_type == "active_habits":
                progress = active_habits_count
            elif ach.criteria_type == "goals_created":
                progress = goals_created
            elif ach.criteria_type == "goals_completed":
                progress = goals_completed

            pct = 0.0
            if is_unlocked:
                pct = 100.0
                progress = max(progress, target)
            elif target > 0:
                pct = round(min(100.0, (progress / target) * 100.0), 1)

            results.append(
                AchievementWithProgress(
                    id=ach.id,
                    code=ach.code,
                    title=ach.title,
                    description=ach.description,
                    icon=ach.icon,
                    category=ach.category,
                    criteria_type=ach.criteria_type,
                    criteria_value=ach.criteria_value,
                    is_unlocked=is_unlocked,
                    unlocked_at=unlocked_record.unlocked_at if unlocked_record else None,
                    progress=progress,
                    target=target,
                    progress_percentage=pct,
                )
            )

        return results

    @classmethod
    def evaluate_streak_achievements(
        cls, db: Session, user_id: uuid.UUID, habit_id: uuid.UUID
    ) -> List[AchievementPublic]:
        """Evaluates streak achievements based on the habit's current streak."""
        habit = HabitRepository.get_by_id(db, habit_id)
        if not habit:
            return []

        streak_achievements = (
            db.query(Achievement)
            .filter(
                Achievement.criteria_type == "streak",
                Achievement.is_active == True,
            )
            .all()
        )

        unlocked: List[AchievementPublic] = []
        for ach in streak_achievements:
            if habit.current_streak >= ach.criteria_value:
                res = AchievementRepository.unlock_achievement(
                    db, user_id=user_id, achievement_id=ach.id, habit_id=habit_id
                )
                if res:
                    unlocked.append(AchievementPublic.model_validate(ach))
        return unlocked

    @classmethod
    def evaluate_completion_achievements(
        cls, db: Session, user_id: uuid.UUID
    ) -> List[AchievementPublic]:
        """Evaluates total completions count achievements."""
        total_completions = (
            db.query(HabitLog).filter(HabitLog.user_id == user_id).count()
        )

        completion_achievements = (
            db.query(Achievement)
            .filter(
                Achievement.criteria_type == "completions",
                Achievement.is_active == True,
            )
            .all()
        )

        unlocked: List[AchievementPublic] = []
        for ach in completion_achievements:
            if total_completions >= ach.criteria_value:
                res = AchievementRepository.unlock_achievement(
                    db, user_id=user_id, achievement_id=ach.id
                )
                if res:
                    unlocked.append(AchievementPublic.model_validate(ach))
        return unlocked

    @classmethod
    def evaluate_habit_achievements(
        cls, db: Session, user_id: uuid.UUID
    ) -> List[AchievementPublic]:
        """Evaluates active habits count achievements."""
        active_habits = HabitRepository.get_user_habits(
            db, user_id=user_id, is_active=True, is_archived=False
        )
        active_count = len(active_habits)

        habit_achievements = (
            db.query(Achievement)
            .filter(
                Achievement.criteria_type == "active_habits",
                Achievement.is_active == True,
            )
            .all()
        )

        unlocked: List[AchievementPublic] = []
        for ach in habit_achievements:
            if active_count >= ach.criteria_value:
                res = AchievementRepository.unlock_achievement(
                    db, user_id=user_id, achievement_id=ach.id
                )
                if res:
                    unlocked.append(AchievementPublic.model_validate(ach))
        return unlocked

    @classmethod
    def evaluate_goal_achievements(
        cls, db: Session, user_id: uuid.UUID
    ) -> List[AchievementPublic]:
        """Evaluates goals created and goals completed achievements."""
        goals_created = (
            db.query(Goal)
            .filter(Goal.user_id == user_id, Goal.is_deleted == False)
            .count()
        )
        goals_completed = (
            db.query(Goal)
            .filter(
                Goal.user_id == user_id,
                Goal.status == "completed",
                Goal.is_deleted == False,
            )
            .count()
        )

        goal_achievements = (
            db.query(Achievement)
            .filter(
                Achievement.category == "goal",
                Achievement.is_active == True,
            )
            .all()
        )

        unlocked: List[AchievementPublic] = []
        for ach in goal_achievements:
            should_unlock = False
            if ach.criteria_type == "goals_created" and goals_created >= ach.criteria_value:
                should_unlock = True
            elif ach.criteria_type == "goals_completed" and goals_completed >= ach.criteria_value:
                should_unlock = True

            if should_unlock:
                res = AchievementRepository.unlock_achievement(
                    db, user_id=user_id, achievement_id=ach.id
                )
                if res:
                    unlocked.append(AchievementPublic.model_validate(ach))
        return unlocked

    @classmethod
    def evaluate_after_habit_completion(
        cls, db: Session, user_id: uuid.UUID, habit_id: uuid.UUID
    ) -> List[AchievementPublic]:
        """
        Orchestrates full achievement evaluation after a habit completion.
        Returns all newly unlocked achievements.
        """
        AchievementRepository.ensure_seeded(db)
        newly_unlocked: List[AchievementPublic] = []

        # 1. Streak achievements
        newly_unlocked.extend(
            cls.evaluate_streak_achievements(db, user_id=user_id, habit_id=habit_id)
        )

        # 2. Completion count achievements
        newly_unlocked.extend(
            cls.evaluate_completion_achievements(db, user_id=user_id)
        )

        # 3. Habit count achievements
        newly_unlocked.extend(
            cls.evaluate_habit_achievements(db, user_id=user_id)
        )

        return newly_unlocked
