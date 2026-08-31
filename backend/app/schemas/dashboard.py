from datetime import date
from typing import List, Optional
from pydantic import BaseModel
from app.schemas.habit import HabitPublic
from app.schemas.goal import GoalPublic


class DashboardUserSummary(BaseModel):
    full_name: Optional[str] = None
    current_date: date
    timezone: str


class TodayProgress(BaseModel):
    total_expected_habits: int
    completed_habits: int
    completion_percentage: float
    habits: List[HabitPublic]


class ConsistencySummary(BaseModel):
    total_active_habits: int
    total_completions_all_time: int
    best_streak_overall: int


class DashboardResponse(BaseModel):
    user: DashboardUserSummary
    today: TodayProgress
    consistency_summary: ConsistencySummary
    goals: List[GoalPublic] = []
