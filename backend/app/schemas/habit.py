from datetime import date, datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, field_validator


class HabitCreate(BaseModel):
    model_config = {"extra": "forbid"}

    title: str
    description: Optional[str] = None
    category: str
    goal_id: Optional[UUID] = None
    frequency_type: str = "daily"
    frequency_days: Optional[List[int]] = None  # [0..6]
    target_value: Optional[float] = None
    target_unit: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    start_date: Optional[date] = None

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()

    @field_validator("frequency_type")
    @classmethod
    def valid_frequency_type(cls, v: str) -> str:
        valid = {"daily", "specific_days", "weekdays", "weekends", "weekly"}
        if v not in valid:
            raise ValueError(f"frequency_type must be one of: {valid}")
        return v


class HabitUpdate(BaseModel):
    model_config = {"extra": "forbid"}

    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    goal_id: Optional[UUID] = None
    frequency_type: Optional[str] = None
    frequency_days: Optional[List[int]] = None
    target_value: Optional[float] = None
    target_unit: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    end_date: Optional[date] = None


class StreakInfo(BaseModel):
    current_streak: int
    best_streak: int
    total_completions: int


class HabitPublic(BaseModel):
    id: UUID
    user_id: UUID
    goal_id: Optional[UUID]
    title: str
    description: Optional[str]
    category: str
    frequency_type: str
    frequency_days: Optional[List[int]]
    target_value: Optional[float]
    target_unit: Optional[str]
    color: Optional[str]
    icon: Optional[str]
    start_date: date
    end_date: Optional[date]
    is_active: bool
    is_archived: bool
    current_streak: int
    best_streak: int
    total_completions: int
    completed_today: Optional[bool] = False
    order_index: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class HabitCompleteRequest(BaseModel):
    model_config = {"extra": "forbid"}

    value: Optional[float] = None
    notes: Optional[str] = None
    completed_date: Optional[date] = None  # Defaults to today in user's timezone


class HabitCompleteResponse(BaseModel):
    log_id: UUID
    habit_id: UUID
    completed_date: date
    streak: StreakInfo
    achievements_unlocked: List[str] = []
