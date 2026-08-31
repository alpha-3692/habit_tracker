# Import all models here so Alembic can discover them for autogenerate
from app.models.user import User
from app.models.goal import Goal
from app.models.habit import Habit
from app.models.habit_log import HabitLog
from app.models.reminder import Reminder
from app.models.achievement import Achievement, UserAchievement
from app.models.subscription import Subscription

__all__ = [
    "User",
    "Goal",
    "Habit",
    "HabitLog",
    "Reminder",
    "Achievement",
    "UserAchievement",
    "Subscription",
]
