"""Habit API endpoints — CRUD, archiving, and habit completions."""
from datetime import date
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.habit import (
    HabitCreate,
    HabitUpdate,
    HabitPublic,
    HabitCompleteRequest,
    HabitCompleteResponse,
)
from app.schemas.history import HabitHistoryResponse
from app.services.habit_service import HabitService
from app.services.history_service import HistoryService

router = APIRouter()


@router.get("", response_model=List[HabitPublic])
async def get_habits(
    is_active: Optional[bool] = Query(None, description="Filter active habits"),
    is_archived: Optional[bool] = Query(None, description="Filter archived habits"),
    goal_id: Optional[UUID] = Query(None, description="Filter by associated goal ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all habits for the authenticated user."""
    return HabitService.get_user_habits(
        db,
        user=current_user,
        is_active=is_active,
        is_archived=is_archived,
        goal_id=goal_id,
    )


@router.post("", response_model=HabitPublic, status_code=status.HTTP_201_CREATED)
async def create_habit(
    payload: HabitCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new habit for the authenticated user."""
    return HabitService.create_habit(db, user=current_user, payload=payload)


@router.get("/{habit_id}", response_model=HabitPublic)
async def get_habit_by_id(
    habit_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific habit by ID."""
    return HabitService.get_habit_by_id(db, user=current_user, habit_id=habit_id)


@router.patch("/{habit_id}", response_model=HabitPublic)
async def update_habit(
    habit_id: UUID,
    payload: HabitUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a habit."""
    return HabitService.update_habit(
        db, user=current_user, habit_id=habit_id, payload=payload
    )


@router.patch("/{habit_id}/archive", response_model=HabitPublic)
async def archive_habit(
    habit_id: UUID,
    is_archived: bool = Query(True, description="True to archive, False to unarchive"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Archive or unarchive a habit."""
    return HabitService.archive_habit(
        db, user=current_user, habit_id=habit_id, is_archived=is_archived
    )


@router.delete("/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_habit(
    habit_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Soft delete a habit."""
    HabitService.delete_habit(db, user=current_user, habit_id=habit_id)
    return None


@router.post("/{habit_id}/complete", response_model=HabitCompleteResponse)
async def complete_habit(
    habit_id: UUID,
    payload: HabitCompleteRequest = HabitCompleteRequest(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark a habit complete for today (or specified past date)."""
    return HabitService.complete_habit(
        db, user=current_user, habit_id=habit_id, payload=payload
    )


@router.get("/{habit_id}/history", response_model=HabitHistoryResponse)
async def get_habit_history(
    habit_id: UUID,
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get day-by-day historical completion status for a specific habit."""
    return HistoryService.get_habit_history(
        db,
        user=current_user,
        habit_id=habit_id,
        start_date=start_date,
        end_date=end_date,
    )
