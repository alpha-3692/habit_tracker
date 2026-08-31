import uuid
from datetime import time, datetime, date
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ReminderCreate(BaseModel):
    habit_id: uuid.UUID
    reminder_time: time
    days_of_week: Optional[List[int]] = Field(
        None,
        description="List of weekday integers (0=Monday, 6=Sunday). None means every due day of habit.",
    )
    is_active: bool = True

    @field_validator("days_of_week")
    @classmethod
    def validate_days(cls, v: Optional[List[int]]) -> Optional[List[int]]:
        if v is not None:
            if not v:
                return None
            for d in v:
                if not (0 <= d <= 6):
                    raise ValueError("Each day in days_of_week must be between 0 (Monday) and 6 (Sunday)")
        return v


class ReminderUpdate(BaseModel):
    reminder_time: Optional[time] = None
    days_of_week: Optional[List[int]] = None
    is_active: Optional[bool] = None

    @field_validator("days_of_week")
    @classmethod
    def validate_days(cls, v: Optional[List[int]]) -> Optional[List[int]]:
        if v is not None:
            for d in v:
                if not (0 <= d <= 6):
                    raise ValueError("Each day in days_of_week must be between 0 (Monday) and 6 (Sunday)")
        return v


class ReminderPublic(BaseModel):
    id: uuid.UUID
    habit_id: uuid.UUID
    habit_title: Optional[str] = None
    habit_category: Optional[str] = None
    user_id: uuid.UUID
    reminder_time: time
    days_of_week: Optional[List[int]] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DueReminderItem(BaseModel):
    reminder_id: uuid.UUID
    habit_id: uuid.UUID
    habit_title: str
    habit_category: str
    user_id: uuid.UUID
    user_timezone: str
    local_time: str
    local_date: date
    message: str

    model_config = ConfigDict(from_attributes=True)


class NextReminderPublic(BaseModel):
    reminder_id: uuid.UUID
    habit_id: uuid.UUID
    habit_title: str
    habit_category: str
    reminder_time: time
    next_occurrence: str  # e.g., "Today at 07:00", "Tomorrow at 07:00", "Mon at 07:00"

    model_config = ConfigDict(from_attributes=True)
