"""User endpoints — profile viewing and updates."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UserPublic, UserUpdate
from app.services.user_service import UserService

router = APIRouter()


@router.get("/me", response_model=UserPublic)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current authenticated user profile."""
    return UserService.get_current_user_profile(current_user)


@router.patch("/me", response_model=UserPublic)
async def update_current_user_profile(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update current user profile."""
    return UserService.update_user_profile(db, current_user, payload)
