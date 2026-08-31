"""Goals API endpoints — Goal CRUD and habit associations."""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.goal import GoalCreate, GoalUpdate, GoalPublic
from app.services.goal_service import GoalService

router = APIRouter()


@router.get("", response_model=List[GoalPublic])
async def get_goals(
    status: Optional[str] = Query(None, description="Filter by goal status (active, completed, archived)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all goals for the authenticated user."""
    return GoalService.get_user_goals(db, user=current_user, status=status)


@router.post("", response_model=GoalPublic, status_code=status.HTTP_201_CREATED)
async def create_goal(
    payload: GoalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new goal for the authenticated user."""
    return GoalService.create_goal(db, user=current_user, payload=payload)


@router.get("/{goal_id}", response_model=GoalPublic)
async def get_goal_by_id(
    goal_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific goal with its associated habit summaries and progress."""
    return GoalService.get_goal_by_id(db, user=current_user, goal_id=goal_id)


@router.patch("/{goal_id}", response_model=GoalPublic)
async def update_goal(
    goal_id: UUID,
    payload: GoalUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update goal properties (title, description, status, target_date)."""
    return GoalService.update_goal(
        db, user=current_user, goal_id=goal_id, payload=payload
    )


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal(
    goal_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Soft delete a goal and safely unlink its associated habits."""
    GoalService.delete_goal(db, user=current_user, goal_id=goal_id)
    return None
