"""Achievement schemas."""

from pydantic import BaseModel, validator
from typing import Optional


class AchievementBase(BaseModel):
    """Base achievement schema."""
    name_ru: str
    name_en: str
    description_ru: str
    description_en: str
    points: int


class AchievementCreate(AchievementBase):
    """Achievement creation schema."""
    
    @validator('points')
    def validate_points(cls, v):
        if v <= 0:
            raise ValueError('Points must be positive')
        return v


class AchievementResponse(AchievementBase):
    """Achievement response schema."""
    id: int
    
    class Config:
        from_attributes = True


class AchievementLocalized(BaseModel):
    """Localized achievement schema."""
    id: int
    name: str
    description: str
    points: int
    
    class Config:
        from_attributes = True