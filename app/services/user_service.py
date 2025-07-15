"""User service."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.models import User, UserAchievement, Achievement
from app.schemas import UserCreate, AchievementLocalized
from app.models.user import LanguageEnum


class UserService:
    """User service for business logic."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_user(self, user: UserCreate) -> User:
        """Create a new user."""
        try:
            # Check if username already exists
            result = await self.db.execute(
                select(User).filter(User.username == user.username)
            )
            existing_user = result.scalar_one_or_none()
            if existing_user:
                raise ValueError("Username already exists")
            
            db_user = User(
                username=user.username,
                language=user.language
            )
            self.db.add(db_user)
            await self.db.commit()
            await self.db.refresh(db_user)
            return db_user
        except Exception as e:
            await self.db.rollback()
            raise e
    
    async def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        result = await self.db.execute(
            select(User).filter(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users."""
        result = await self.db.execute(
            select(User).offset(skip).limit(limit)
        )
        return result.scalars().all()
    
    async def get_user_achievements(self, user_id: int) -> List[AchievementLocalized]:
        """Get user achievements in user's language."""
        user = await self.get_user(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Get user's achievements with localized names
        result = await self.db.execute(
            select(
                Achievement.id,
                Achievement.name_ru,
                Achievement.name_en,
                Achievement.description_ru,
                Achievement.description_en,
                Achievement.points,
                UserAchievement.awarded_at
            ).join(
                UserAchievement, Achievement.id == UserAchievement.achievement_id
            ).filter(
                UserAchievement.user_id == user_id
            )
        )
        achievements = result.all()
        
        # Localize based on user's language
        localized_achievements = []
        for achievement in achievements:
            if user.language == LanguageEnum.RU:
                name = achievement.name_ru
                description = achievement.description_ru
            else:
                name = achievement.name_en
                description = achievement.description_en
            
            localized_achievements.append(AchievementLocalized(
                id=achievement.id,
                name=name,
                description=description,
                points=achievement.points
            ))
        
        return localized_achievements