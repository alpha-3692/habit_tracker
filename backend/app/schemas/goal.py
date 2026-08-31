from datetime import date, datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, ConfigDict, field_validator


class GoalCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    description: Optional[str] = None
    category: str
    target_date: Optional[date] = None

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()


class GoalUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    target_date: Optional[date] = None

    @field_validator("status")
    @classmethod
    def valid_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            valid = {"active", "completed", "archived"}
            if v not in valid:
                raise ValueError(f"Status must be one of: {valid}")
        return v


class GoalHabitSummary(BaseModel):
    id: UUID
    title: str
    category: str
    current_streak: int
    completion_percentage: float

    model_config = ConfigDict(from_attributes=True)


class GoalPublic(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    description: Optional[str]
    category: str
    status: str
    target_date: Optional[date]
    habit_count: int
    progress_percentage: float
    habits: List[GoalHabitSummary] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
