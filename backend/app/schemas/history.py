from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.habit import HabitPublic


class DayHistory(BaseModel):
    date: date
    is_due: bool
    is_completed: bool
    value: Optional[float] = None
    notes: Optional[str] = None
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class HabitHistoryResponse(BaseModel):
    habit: HabitPublic
    start_date: date
    end_date: date
    days: List[DayHistory]

    model_config = ConfigDict(from_attributes=True)


class CalendarDaySummary(BaseModel):
    date: date
    expected: int
    completed: int
    percentage: float

    model_config = ConfigDict(from_attributes=True)


class CalendarResponse(BaseModel):
    start_date: date
    end_date: date
    days: List[CalendarDaySummary]

    model_config = ConfigDict(from_attributes=True)
