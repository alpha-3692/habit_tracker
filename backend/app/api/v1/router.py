from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, habits, goals, dashboard, analytics, achievements, reminders

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(habits.router, prefix="/habits", tags=["Habits"])
api_router.include_router(goals.router, prefix="/goals", tags=["Goals"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(achievements.router, prefix="/achievements", tags=["Achievements"])
api_router.include_router(reminders.router, prefix="/reminders", tags=["Reminders"])


