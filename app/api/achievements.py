"""Achievement API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.schemas import AchievementCreate, AchievementResponse, UserAchievementCreate
from app.services.achievement_service import AchievementService

router = APIRouter()


@router.post("/", response_model=AchievementResponse, status_code=status.HTTP_201_CREATED)
async def create_achievement(achievement: AchievementCreate, db: AsyncSession = Depends(get_db)):
    """Create a new achievement."""
    service = AchievementService(db)
    return await service.create_achievement(achievement)


@router.get("/", response_model=List[AchievementResponse])
async def get_achievements(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """Get all achievements."""
    service = AchievementService(db)
    return await service.get_achievements(skip=skip, limit=limit)


@router.get("/{achievement_id}", response_model=AchievementResponse)
async def get_achievement(achievement_id: int, db: AsyncSession = Depends(get_db)):
    """Get achievement by ID."""
    service = AchievementService(db)
    achievement = await service.get_achievement(achievement_id)
    if not achievement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Achievement not found"
        )
    return achievement


@router.post("/award", status_code=status.HTTP_201_CREATED)
async def award_achievement(award: UserAchievementCreate, db: AsyncSession = Depends(get_db)):
    """Award achievement to user."""
    try:
        service = AchievementService(db)
        return await service.award_achievement(award)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )