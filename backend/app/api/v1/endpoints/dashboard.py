"""Dashboard API endpoint — aggregated daily overview."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.dashboard import DashboardResponse
from app.services.dashboard_service import DashboardService

router = APIRouter()


@router.get("", response_model=DashboardResponse)
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get aggregated daily dashboard view for the authenticated user.
    Returns today's habits, completion state, progress percentage,
    and overall consistency metrics in the user's timezone.
    """
    return DashboardService.get_dashboard_data(db, current_user)
