"""Achievement API endpoints."""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.achievement import AchievementPublic, AchievementWithProgress
from app.services.achievement_service import AchievementService

router = APIRouter()


@router.get("", response_model=List[AchievementPublic])
async def get_all_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get the complete system achievement catalog.
    Requires authentication.
    """
    return AchievementService.get_all_achievements(db)


@router.get("/me", response_model=List[AchievementWithProgress])
async def get_my_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get achievements for the current user including unlocked status,
    unlocked_at timestamp, and deterministic progress towards locked goals.
    """
    return AchievementService.get_user_achievements(db, user=current_user)
