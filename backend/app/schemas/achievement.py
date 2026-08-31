import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class AchievementPublic(BaseModel):
    id: uuid.UUID
    code: str
    title: str
    description: str
    icon: Optional[str] = None
    category: str
    criteria_type: str
    criteria_value: int
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)


class UserAchievementPublic(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    achievement_id: uuid.UUID
    habit_id: Optional[uuid.UUID] = None
    unlocked_at: datetime
    achievement: Optional[AchievementPublic] = None

    model_config = ConfigDict(from_attributes=True)


class AchievementWithProgress(BaseModel):
    id: uuid.UUID
    code: str
    title: str
    description: str
    icon: Optional[str] = None
    category: str
    criteria_type: str
    criteria_value: int
    is_unlocked: bool
    unlocked_at: Optional[datetime] = None
    progress: int
    target: int
    progress_percentage: float

    model_config = ConfigDict(from_attributes=True)
