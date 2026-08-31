"""Analytics, trends, calendar, and behavioral insights endpoints."""
from datetime import date
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.history import CalendarResponse
from app.schemas.analytics import AnalyticsTrendsResponse
from app.services.history_service import HistoryService
from app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/calendar", response_model=CalendarResponse)
async def get_calendar_summary(
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    habit_id: Optional[UUID] = Query(None, description="Filter calendar by specific habit"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get daily expected vs completed habits and consistency percentage for a date range.
    Authoritatively aggregates across all active habits (or single filtered habit).
    """
    return HistoryService.get_calendar_summary(
        db,
        user=current_user,
        start_date=start_date,
        end_date=end_date,
        habit_id=habit_id,
    )


@router.get("/trends", response_model=AnalyticsTrendsResponse)
async def get_analytics_trends(
    days: int = Query(30, description="Rolling time range in days (7 to 365)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get aggregate habit consistency trends, day-of-week performance, category breakdowns,
    momentum scoring, and deterministic behavioral insights.
    """
    return AnalyticsService.get_trends(db, user=current_user, days=days)
