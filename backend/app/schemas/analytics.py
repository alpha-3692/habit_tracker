from datetime import date
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class WeeklyTrendItem(BaseModel):
    week_start: date
    week_end: date
    expected: int
    completed: int
    percentage: float

    model_config = ConfigDict(from_attributes=True)


class DayOfWeekItem(BaseModel):
    day_name: str
    day_index: int  # 0 = Monday, 6 = Sunday
    expected: int
    completed: int
    percentage: float

    model_config = ConfigDict(from_attributes=True)


class CategoryPerformanceItem(BaseModel):
    category: str
    habit_count: int
    expected: int
    completed: int
    percentage: float

    model_config = ConfigDict(from_attributes=True)


class BehaviorInsight(BaseModel):
    type: str  # best_day | weakest_day | weekend_drop | streak_highlight | category_leader | momentum
    title: str
    description: str
    impact: str  # positive | neutral | warning

    model_config = ConfigDict(from_attributes=True)


class AnalyticsTrendsResponse(BaseModel):
    time_range_days: int
    overall_consistency: float
    total_habits_tracked: int
    total_completions: int
    momentum_score: int  # 0 to 100
    weekly_trends: List[WeeklyTrendItem]
    day_of_week: List[DayOfWeekItem]
    category_breakdown: List[CategoryPerformanceItem]
    insights: List[BehaviorInsight]

    model_config = ConfigDict(from_attributes=True)
