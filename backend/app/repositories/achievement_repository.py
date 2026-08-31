import uuid
from typing import List, Optional, Set
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError

from app.models.achievement import Achievement, UserAchievement

INITIAL_ACHIEVEMENTS = [
    # ── Streak Achievements ───────────────────────────────────────────
    {
        "code": "streak_7",
        "title": "7-Day Streak",
        "description": "Maintained a streak for 7 consecutive days",
        "icon": "flame",
        "category": "streak",
        "criteria_type": "streak",
        "criteria_value": 7,
    },
    {
        "code": "streak_14",
        "title": "14-Day Streak",
        "description": "Maintained a streak for 14 consecutive days",
        "icon": "flame",
        "category": "streak",
        "criteria_type": "streak",
        "criteria_value": 14,
    },
    {
        "code": "streak_30",
        "title": "30-Day Streak",
        "description": "Maintained a streak for 30 consecutive days",
        "icon": "flame",
        "category": "streak",
        "criteria_type": "streak",
        "criteria_value": 30,
    },
    {
        "code": "streak_60",
        "title": "60-Day Streak",
        "description": "Maintained a streak for 60 consecutive days",
        "icon": "flame",
        "category": "streak",
        "criteria_type": "streak",
        "criteria_value": 60,
    },
    {
        "code": "streak_100",
        "title": "Centurion Streak",
        "description": "Maintained a streak for 100 consecutive days",
        "icon": "flame",
        "category": "streak",
        "criteria_type": "streak",
        "criteria_value": 100,
    },
    # ── Completion Achievements ───────────────────────────────────────
    {
        "code": "first_completion",
        "title": "First Step",
        "description": "Completed your very first habit",
        "icon": "check-circle",
        "category": "completion",
        "criteria_type": "completions",
        "criteria_value": 1,
    },
    {
        "code": "completions_10",
        "title": "Double Digits",
        "description": "Reached 10 total habit completions",
        "icon": "check-circle",
        "category": "completion",
        "criteria_type": "completions",
        "criteria_value": 10,
    },
    {
        "code": "completions_50",
        "title": "Half Century",
        "description": "Reached 50 total habit completions",
        "icon": "check-circle",
        "category": "completion",
        "criteria_type": "completions",
        "criteria_value": 50,
    },
    {
        "code": "completions_100",
        "title": "Century Club",
        "description": "Reached 100 total habit completions",
        "icon": "award",
        "category": "completion",
        "criteria_type": "completions",
        "criteria_value": 100,
    },
    {
        "code": "completions_500",
        "title": "Master of Habit",
        "description": "Reached 500 total habit completions",
        "icon": "award",
        "category": "completion",
        "criteria_type": "completions",
        "criteria_value": 500,
    },
    {
        "code": "completions_1000",
        "title": "Legendary Discipline",
        "description": "Reached 1000 total habit completions",
        "icon": "crown",
        "category": "completion",
        "criteria_type": "completions",
        "criteria_value": 1000,
    },
    # ── Habit Achievements ────────────────────────────────────────────
    {
        "code": "first_habit",
        "title": "Habit Builder",
        "description": "Created your first active habit",
        "icon": "plus-circle",
        "category": "habit",
        "criteria_type": "active_habits",
        "criteria_value": 1,
    },
    {
        "code": "active_habits_3",
        "title": "Trio Focus",
        "description": "Created 3 active habits",
        "icon": "layers",
        "category": "habit",
        "criteria_type": "active_habits",
        "criteria_value": 3,
    },
    {
        "code": "active_habits_5",
        "title": "Solid Foundation",
        "description": "Created 5 active habits",
        "icon": "layers",
        "category": "habit",
        "criteria_type": "active_habits",
        "criteria_value": 5,
    },
    {
        "code": "active_habits_10",
        "title": "Power Routine",
        "description": "Created 10 active habits",
        "icon": "zap",
        "category": "habit",
        "criteria_type": "active_habits",
        "criteria_value": 10,
    },
    # ── Goal Achievements ─────────────────────────────────────────────
    {
        "code": "first_goal",
        "title": "Visionary",
        "description": "Created your first long-term goal",
        "icon": "target",
        "category": "goal",
        "criteria_type": "goals_created",
        "criteria_value": 1,
    },
    {
        "code": "first_goal_completed",
        "title": "Mission Accomplished",
        "description": "Completed your first goal",
        "icon": "flag",
        "category": "goal",
        "criteria_type": "goals_completed",
        "criteria_value": 1,
    },
    {
        "code": "goals_completed_3",
        "title": "Triple Victory",
        "description": "Completed 3 goals",
        "icon": "trophy",
        "category": "goal",
        "criteria_type": "goals_completed",
        "criteria_value": 3,
    },
]


class AchievementRepository:
    @staticmethod
    def ensure_seeded(db: Session) -> None:
        """Seeds the standard achievement catalog into the database if not present."""
        existing_codes = {a.code for a in db.query(Achievement).all()}
        new_achievements = []
        for ach in INITIAL_ACHIEVEMENTS:
            if ach["code"] not in existing_codes:
                new_achievements.append(
                    Achievement(
                        id=uuid.uuid4(),
                        code=ach["code"],
                        title=ach["title"],
                        description=ach["description"],
                        icon=ach["icon"],
                        category=ach["category"],
                        criteria_type=ach["criteria_type"],
                        criteria_value=ach["criteria_value"],
                        is_active=True,
                    )
                )
        if new_achievements:
            db.add_all(new_achievements)
            db.commit()

    @staticmethod
    def get_all(db: Session, is_active: bool = True) -> List[Achievement]:
        """Returns all system achievements."""
        query = db.query(Achievement)
        if is_active is not None:
            query = query.filter(Achievement.is_active == is_active)
        return query.order_by(Achievement.category, Achievement.criteria_value).all()

    @staticmethod
    def get_by_code(db: Session, code: str) -> Optional[Achievement]:
        """Fetch an achievement definition by unique code."""
        return db.query(Achievement).filter(Achievement.code == code).first()

    @staticmethod
    def get_user_unlocked_achievements(
        db: Session, user_id: uuid.UUID
    ) -> List[UserAchievement]:
        """Returns all unlocked achievements for a user."""
        return (
            db.query(UserAchievement)
            .options(joinedload(UserAchievement.achievement))
            .filter(UserAchievement.user_id == user_id)
            .order_by(UserAchievement.unlocked_at.desc())
            .all()
        )

    @staticmethod
    def get_user_unlocked_achievement_ids(
        db: Session, user_id: uuid.UUID
    ) -> Set[uuid.UUID]:
        """Returns set of achievement IDs unlocked by user."""
        rows = (
            db.query(UserAchievement.achievement_id)
            .filter(UserAchievement.user_id == user_id)
            .all()
        )
        return {r[0] for r in rows}

    @staticmethod
    def unlock_achievement(
        db: Session,
        user_id: uuid.UUID,
        achievement_id: uuid.UUID,
        habit_id: Optional[uuid.UUID] = None,
    ) -> Optional[UserAchievement]:
        """
        Idempotently unlocks an achievement for a user.
        Returns the UserAchievement record, or None if already unlocked.
        """
        # Check if already unlocked
        existing = (
            db.query(UserAchievement)
            .filter(
                UserAchievement.user_id == user_id,
                UserAchievement.achievement_id == achievement_id,
            )
            .first()
        )
        if existing:
            return None

        user_achievement = UserAchievement(
            id=uuid.uuid4(),
            user_id=user_id,
            achievement_id=achievement_id,
            habit_id=habit_id,
        )
        try:
            db.add(user_achievement)
            db.commit()
            db.refresh(user_achievement)
            return user_achievement
        except IntegrityError:
            db.rollback()
            return None
