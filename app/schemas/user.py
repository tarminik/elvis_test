"""User schemas."""

from pydantic import BaseModel
from app.models.user import LanguageEnum


class UserBase(BaseModel):
    """Base user schema."""
    username: str
    language: LanguageEnum = LanguageEnum.RU


class UserCreate(UserBase):
    """User creation schema."""
    pass


class UserResponse(UserBase):
    """User response schema."""
    id: int
    
    class Config:
        from_attributes = True