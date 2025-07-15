"""Achievement service."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.models import Achievement, UserAchievement, User
from app.schemas import AchievementCreate, UserAchievementCreate


class AchievementService:
    """Achievement service for business logic."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_achievement(self, achievement: AchievementCreate) -> Achievement:
        """Create a new achievement."""
        db_achievement = Achievement(
            name_ru=achievement.name_ru,
            name_en=achievement.name_en,
            description_ru=achievement.description_ru,
            description_en=achievement.description_en,
            points=achievement.points
        )
        self.db.add(db_achievement)
        await self.db.commit()
        await self.db.refresh(db_achievement)
        return db_achievement
    
    async def get_achievement(self, achievement_id: int) -> Optional[Achievement]:
        """Get achievement by ID."""
        result = await self.db.execute(
            select(Achievement).filter(Achievement.id == achievement_id)
        )
        return result.scalar_one_or_none()
    
    async def get_achievements(self, skip: int = 0, limit: int = 100) -> List[Achievement]:
        """Get all achievements."""
        result = await self.db.execute(
            select(Achievement).offset(skip).limit(limit)
        )
        return result.scalars().all()
    
    async def award_achievement(self, award: UserAchievementCreate) -> UserAchievement:
        """Award achievement to user."""
        # Check if user exists
        user_result = await self.db.execute(
            select(User).filter(User.id == award.user_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            raise ValueError("User not found")
        
        # Check if achievement exists
        achievement_result = await self.db.execute(
            select(Achievement).filter(Achievement.id == award.achievement_id)
        )
        achievement = achievement_result.scalar_one_or_none()
        if not achievement:
            raise ValueError("Achievement not found")
        
        # Check if user already has this achievement
        existing_result = await self.db.execute(
            select(UserAchievement).filter(
                UserAchievement.user_id == award.user_id,
                UserAchievement.achievement_id == award.achievement_id
            )
        )
        existing_award = existing_result.scalar_one_or_none()
        
        if existing_award:
            raise ValueError("User already has this achievement")
        
        # Create new user achievement
        db_user_achievement = UserAchievement(
            user_id=award.user_id,
            achievement_id=award.achievement_id
        )
        self.db.add(db_user_achievement)
        await self.db.commit()
        await self.db.refresh(db_user_achievement)
        return db_user_achievement