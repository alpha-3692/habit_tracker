"""Reminder API endpoints — CRUD, list, and next reminder calculations."""
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.reminder import (
    ReminderCreate,
    ReminderUpdate,
    ReminderPublic,
    NextReminderPublic,
)
from app.services.reminder_service import ReminderService

router = APIRouter()


@router.post("", response_model=ReminderPublic, status_code=status.HTTP_201_CREATED)
async def create_reminder(
    payload: ReminderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new habit reminder."""
    return ReminderService.create_reminder(db, user=current_user, payload=payload)


@router.get("", response_model=List[ReminderPublic])
async def get_reminders(
    is_active: Optional[bool] = Query(None, description="Filter active/disabled reminders"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all reminders configured by the current user."""
    return ReminderService.get_user_reminders(db, user=current_user, is_active=is_active)


@router.get("/next", response_model=Optional[NextReminderPublic])
async def get_next_reminder(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the next upcoming reminder occurrence for the current user."""
    return ReminderService.get_next_reminder_for_user(db, user=current_user)


@router.get("/{reminder_id}", response_model=ReminderPublic)
async def get_reminder(
    reminder_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific reminder by ID."""
    return ReminderService.get_reminder_by_id(
        db, user=current_user, reminder_id=reminder_id
    )


@router.patch("/{reminder_id}", response_model=ReminderPublic)
async def update_reminder(
    reminder_id: uuid.UUID,
    payload: ReminderUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a reminder."""
    return ReminderService.update_reminder(
        db, user=current_user, reminder_id=reminder_id, payload=payload
    )


@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reminder(
    reminder_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a reminder."""
    ReminderService.delete_reminder(db, user=current_user, reminder_id=reminder_id)
    return None
