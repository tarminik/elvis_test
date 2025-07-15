"""Statistics API endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.statistics_service import StatisticsService

router = APIRouter()


@router.get("/top-by-achievements")
async def get_top_by_achievements(db: AsyncSession = Depends(get_db)):
    """Get user with most achievements."""
    service = StatisticsService(db)
    return await service.get_top_by_achievements()


@router.get("/top-by-points")
async def get_top_by_points(db: AsyncSession = Depends(get_db)):
    """Get user with most points."""
    service = StatisticsService(db)
    return await service.get_top_by_points()


@router.get("/min-max-points-difference")
async def get_min_max_points_difference(db: AsyncSession = Depends(get_db)):
    """Get users with min and max points difference."""
    service = StatisticsService(db)
    return await service.get_min_max_points_difference()


@router.get("/7-day-streak-users")
async def get_7_day_streak_users(db: AsyncSession = Depends(get_db)):
    """Get users with 7-day achievement streaks."""
    service = StatisticsService(db)
    return await service.get_7_day_streak_users()