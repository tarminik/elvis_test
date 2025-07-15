"""User achievement schemas."""

from pydantic import BaseModel, ConfigDict
from datetime import datetime


class UserAchievementBase(BaseModel):
    """Base user achievement schema."""
    user_id: int
    achievement_id: int


class UserAchievementCreate(UserAchievementBase):
    """User achievement creation schema."""
    pass


class UserAchievementResponse(UserAchievementBase):
    """User achievement response schema."""
    id: int
    awarded_at: datetime
    
    model_config = ConfigDict(from_attributes=True)